import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
import os
from .models import Order, OrderItem

LAPTOP_URL = os.environ.get('LAPTOP_SERVICE_URL', 'http://laptop-service:8000')
CLOTHES_URL = os.environ.get('CLOTHES_SERVICE_URL', 'http://clothes-service:8000')
PAYMENT_URL = os.environ.get('PAYMENT_SERVICE_URL', 'http://payment-service:8000')
SHIPPING_URL = os.environ.get('SHIPPING_SERVICE_URL', 'http://shipping-service:8000')

@api_view(['GET', 'POST'])
def orders_list_create(request):
    if request.method == 'GET':
        orders = [o.to_dict() for o in Order.objects.all().order_by('-created_at')]
        return Response(orders)
        
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id', 1)
        items = data.get('items', [])
        
        if not items:
            return Response({'error': 'No items in order'}, status=400)
            
        # 1. Create Order in PENDING state
        order = Order.objects.create(user_id=user_id, status='RESERVING')
        total = 0
        
        for item in items:
            p_id = item.get('product_id')
            p_type = item.get('type') # laptops or clothes
            qty = item.get('quantity', 1)
            price = item.get('price', 0) 
            OrderItem.objects.create(order=order, product_id=str(p_id), product_type=p_type, quantity=qty, price_snapshot=price)
            total += float(price) * qty
            
        order.total_amount = total
        order.save()
        
        # 2. Reserve Stock using SAGA Orchestrator
        reserve_failed = False
        failed_item = None
        for item in items:
            t_type = item['type'].strip('s') + 's' # Ensure plural form 'laptops'
            target_url = LAPTOP_URL if t_type == 'laptops' else CLOTHES_URL
            try:
                res = requests.post(f"{target_url}/{t_type}/{item['product_id']}/reserve", json={'quantity': item['quantity']}, timeout=5)
                if not res.ok:
                    reserve_failed = True
                    failed_item = item
                    break
            except Exception as e:
                print('Reservation request error:', e)
                reserve_failed = True
                failed_item = item
                break
                
        if reserve_failed:
            # Rollback: Release whatever was reserved successfully (Skipping for mockup simplicity, just fail the order)
            order.status = 'FAILED_STOCK'
            order.save()
            return Response({'error': f'Stock Reservation Failed for {failed_item.get("product_id")}', 'order_id': str(order.id)}, status=400)
            
        # 3. Stock OK -> Call Payment Service
        order.status = 'PAYMENT_PENDING'
        order.save()
        
        try:
            pay_payload = {
                'order_id': str(order.id),
                'amount': float(order.total_amount)
            }
            pay_res = requests.post(f"{PAYMENT_URL}/payments", json=pay_payload, timeout=5)
            if pay_res.ok:
                pay_data = pay_res.json()
                order.save()
                return Response({'msg': 'Order created and stock reserved', 'order': order.to_dict(), 'payment_url': pay_data.get('payment_url')})
            else:
                order.status = 'FAILED_PAYMENT_INIT'
                order.save()
                return Response({'error': 'Payment Service Integration Failed'}, status=500)
        except Exception as e:
            # Automatically fail if payment gateway is unreachable
            order.status = 'FAILED_PAYMENT_INIT'
            order.save()
            return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def order_detail(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        return Response(order.to_dict())
    except Order.DoesNotExist:
        return Response({'error': 'Not Found'}, status=404)

@api_view(['POST'])
def payment_callback(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        status = data.get('status')
        
        order = Order.objects.get(id=order_id)
        if order.payment_status == status:
            return Response({'msg': 'Already processed'})
            
        order.payment_status = status
        
        if status == 'SUCCESS':
            order.status = 'PROCESSING'
            # 4. Success -> Create Shipment
            try:
                ship_payload = {'order_id': str(order.id), 'address': data.get('address', 'Mặc định')}
                # Non-blocking or simple block
                requests.post(f"{SHIPPING_URL}/shipments", json=ship_payload, timeout=5)
            except Exception as e:
                print("Shipping creation failed:", e)
        else:
            # 5. SAGA Rollback: Release Stock
            order.status = 'FAILED_PAYMENT'
            for item in order.items.all():
                t_type = item.product_type.strip('s') + 's'
                target_url = LAPTOP_URL if t_type == 'laptops' else CLOTHES_URL
                try:
                    requests.post(f"{target_url}/{t_type}/{item.product_id}/release", json={'quantity': item.quantity}, timeout=5)
                except Exception:
                    pass
                    
        order.save()
        return Response({'msg': 'Payment callback processed', 'order_status': order.status})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def shipping_callback(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        status = data.get('status')
        order = Order.objects.get(id=order_id)
        order.shipping_status = status
        if status == 'DELIVERED':
            order.status = 'COMPLETED'
        order.save()
        return Response({'msg': 'Shipping status updated'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

def health_check(request):
    return JsonResponse({'status': 'order service ok'})
