from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
import os
from kafka import KafkaProducer
from .models import Mobile

def broadcast_product_update(action, product_dict):
    try:
        kafka_broker = os.environ.get('KAFKA_BROKER', 'kafka:9092')
        producer = KafkaProducer(
            bootstrap_servers=kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        msg = product_dict.copy()
        msg['action'] = action
        producer.send('product_updates', msg)
        producer.flush()
    except Exception as e:
        print(f"Failed to produce message: {e}")

def health_check(request):
    return JsonResponse({'status': 'mobile service ok'})

@api_view(['GET'])
def mobile_count(request):
    return Response({'count': Mobile.objects.count()})

@api_view(['GET', 'POST'])
def mobile_list_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mobile = Mobile.objects.create(
            name=data.get('name', 'Unknown'), 
            brand=data.get('brand', 'Unknown'),
            image_url=data.get('image_url', ''),
            price=data.get('price', 0),
            quantity=data.get('quantity', 10)
        )
        msg_dict = mobile.to_dict()
        msg_dict['category'] = 'mobile'
        broadcast_product_update('create', msg_dict)
        return Response({'msg': 'Mobile created', 'id': mobile.id})
    mobiles = [l.to_dict() for l in Mobile.objects.all()]
    return Response(mobiles)

@api_view(['PUT', 'DELETE'])
def mobile_detail(request, pk):
    try:
        mobile = Mobile.objects.get(pk=pk)
    except Mobile.DoesNotExist:
        return Response({'msg': 'Not Found'}, status=404)
        
    if request.method == 'PUT':
        data = json.loads(request.body)
        mobile.name = data.get('name', mobile.name)
        mobile.brand = data.get('brand', mobile.brand)
        mobile.image_url = data.get('image_url', mobile.image_url)
        mobile.price = data.get('price', mobile.price)
        mobile.quantity = data.get('quantity', mobile.quantity)
        mobile.save()
        msg_dict = mobile.to_dict()
        msg_dict['category'] = 'mobile'
        broadcast_product_update('update', msg_dict)
        return Response({'msg': f'Mobile {pk} updated', 'mobile': mobile.to_dict()})
        
    mobile.delete()
    return Response({'msg': f'Mobile {pk} deleted'})

@api_view(['POST'])
def mobile_reserve(request, pk):
    try:
        mobile = Mobile.objects.get(pk=pk)
        qty = int(json.loads(request.body).get('quantity', 1))
        if mobile.quantity >= qty:
            mobile.quantity -= qty
            mobile.save()
            return Response({'msg': 'Reserved successfully'})
        return Response({'error': 'Out of stock or insufficient quantity'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def mobile_release(request, pk):
    try:
        mobile = Mobile.objects.get(pk=pk)
        qty = int(json.loads(request.body).get('quantity', 1))
        mobile.quantity += qty
        mobile.save()
        return Response({'msg': 'Released successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def mobile_confirm(request, pk):
    return Response({'msg': 'Confirmed successfully'})
