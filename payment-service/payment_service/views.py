import requests
import uuid
import os
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Payment

ORDER_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8000')

@api_view(['POST'])
def create_payment(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        amount = data.get('amount')
        
        payment = Payment.objects.create(order_id=order_id, amount=amount, status='PENDING')
        # Generate mock payment url
        payment_url = f"http://localhost:8000/payments/checkout?pay_id={payment.id}"
        
        return Response({'msg': 'Payment created', 'payment_id': str(payment.id), 'payment_url': payment_url})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def payment_gateway_callback(request):
    try:
        data = json.loads(request.body)
        pay_id = data.get('payment_id')
        action = data.get('action', 'SUCCESS')
        
        payment = Payment.objects.get(id=pay_id)
        if payment.status != 'PENDING':
            return Response({'msg': 'Already processed'})
            
        payment.status = action
        payment.transaction_id = str(uuid.uuid4())
        payment.save()
        
        requests.post(f"{ORDER_URL}/orders/payment-callback", json={
            'order_id': payment.order_id,
            'status': action,
            'transaction_id': payment.transaction_id
        }, timeout=5)
        
        return Response({'msg': f'Payment {action} processed.'})
    except Payment.DoesNotExist:
        return Response({'error': 'Not Found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def health_check(request):
    return JsonResponse({'status': 'payment service ok'})
