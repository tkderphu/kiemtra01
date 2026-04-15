from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
import os
from kafka import KafkaProducer
from .models import Clothes

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
    return JsonResponse({'status': 'clothes service ok'})

@api_view(['GET'])
def clothes_count(request):
    return Response({'count': Clothes.objects.count()})

@api_view(['GET', 'POST'])
def clothes_list_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        c = Clothes.objects.create(
            name=data.get('name', 'Unknown'), 
            brand=data.get('brand', 'Unknown'),
            image_url=data.get('image_url', ''),
            price=data.get('price', 0),
            quantity=data.get('quantity', 10)
        )
        msg_dict = c.to_dict()
        msg_dict['category'] = 'clothes'
        broadcast_product_update('create', msg_dict)
        return Response({'msg': 'Clothes created', 'id': c.id})
    clothes = [c.to_dict() for c in Clothes.objects.all()]
    return Response(clothes)

@api_view(['PUT', 'DELETE'])
def clothes_detail(request, pk):
    try:
        c = Clothes.objects.get(pk=pk)
    except Clothes.DoesNotExist:
        return Response({'msg': 'Not Found'}, status=404)
        
    if request.method == 'PUT':
        data = json.loads(request.body)
        c.name = data.get('name', c.name)
        c.brand = data.get('brand', c.brand)
        c.image_url = data.get('image_url', c.image_url)
        c.price = data.get('price', c.price)
        c.quantity = data.get('quantity', c.quantity)
        c.save()
        msg_dict = c.to_dict()
        msg_dict['category'] = 'clothes'
        broadcast_product_update('update', msg_dict)
        return Response({'msg': f'Clothes {pk} updated', 'clothes': c.to_dict()})
        
    c.delete()
    return Response({'msg': f'Clothes {pk} deleted'})

@api_view(['POST'])
def clothes_reserve(request, pk):
    try:
        c = Clothes.objects.get(pk=pk)
        qty = int(json.loads(request.body).get('quantity', 1))
        if c.quantity >= qty:
            c.quantity -= qty
            c.save()
            return Response({'msg': 'Reserved successfully'})
        return Response({'error': 'Out of stock or insufficient quantity'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def clothes_release(request, pk):
    try:
        c = Clothes.objects.get(pk=pk)
        qty = int(json.loads(request.body).get('quantity', 1))
        c.quantity += qty
        c.save()
        return Response({'msg': 'Released successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def clothes_confirm(request, pk):
    return Response({'msg': 'Confirmed successfully'})
