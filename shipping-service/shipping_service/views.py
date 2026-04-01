import requests
import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Shipment

ORDER_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8000')

@api_view(['GET', 'POST'])
def shipments_list_create(request):
    if request.method == 'GET':
        shipments = [s.to_dict() for s in Shipment.objects.all().order_by('-created_at')]
        return Response(shipments)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            address = data.get('address', 'Mặc định')
            
            shipment = Shipment.objects.create(order_id=order_id, address=address)
            return Response({'msg': 'Shipment created', 'tracking_number': shipment.tracking_number})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

@api_view(['PATCH'])
def shipment_update_status(request, pk):
    try:
        shipment = Shipment.objects.get(pk=pk)
        data = json.loads(request.body)
        new_status = data.get('status')
        if not new_status:
            return Response({'error': 'Missing status'}, status=400)
            
        shipment.status = new_status
        shipment.save()
        
        requests.post(f"{ORDER_URL}/orders/shipping-callback", json={
            'order_id': shipment.order_id,
            'status': new_status
        }, timeout=5)
        
        return Response({'msg': f'Status updated to {new_status}'})
    except Shipment.DoesNotExist:
        return Response({'error': 'Not Found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def health_check(request):
    return JsonResponse({'status': 'shipping service ok'})
