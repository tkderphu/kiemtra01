from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
import os
from kafka import KafkaProducer
from .models import Laptop

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
    return JsonResponse({'status': 'laptop service ok'})

@api_view(['GET'])
def laptop_count(request):
    return Response({'count': Laptop.objects.count()})

@api_view(['GET', 'POST'])
def laptop_list_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        laptop = Laptop.objects.create(
            name=data.get('name', 'Unknown'), 
            brand=data.get('brand', 'Unknown'),
            image_url=data.get('image_url', ''),
            price=data.get('price', 0),
            quantity=data.get('quantity', 10)
        )
        msg_dict = laptop.to_dict()
        msg_dict['category'] = 'laptop'
        broadcast_product_update('create', msg_dict)
        return Response({'msg': 'Laptop created', 'id': laptop.id})
    laptops = [l.to_dict() for l in Laptop.objects.all()]
    return Response(laptops)

@api_view(['PUT', 'DELETE'])
def laptop_detail(request, pk):
    try:
        laptop = Laptop.objects.get(pk=pk)
    except Laptop.DoesNotExist:
        return Response({'msg': 'Not Found'}, status=404)
        
    if request.method == 'PUT':
        data = json.loads(request.body)
        laptop.name = data.get('name', laptop.name)
        laptop.brand = data.get('brand', laptop.brand)
        laptop.image_url = data.get('image_url', laptop.image_url)
        laptop.price = data.get('price', laptop.price)
        laptop.quantity = data.get('quantity', laptop.quantity)
        laptop.save()
        msg_dict = laptop.to_dict()
        msg_dict['category'] = 'laptop'
        broadcast_product_update('update', msg_dict)
        return Response({'msg': f'Laptop {pk} updated', 'laptop': laptop.to_dict()})
        
    laptop.delete()
    return Response({'msg': f'Laptop {pk} deleted'})

@api_view(['POST'])
def laptop_reserve(request, pk):
    try:
        laptop = Laptop.objects.get(pk=pk)
        qty = int(json.loads(request.body).get('quantity', 1))
        if laptop.quantity >= qty:
            laptop.quantity -= qty
            laptop.save()
            return Response({'msg': 'Reserved successfully'})
        return Response({'error': 'Out of stock or insufficient quantity'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def laptop_release(request, pk):
    try:
        laptop = Laptop.objects.get(pk=pk)
        qty = int(json.loads(request.body).get('quantity', 1))
        laptop.quantity += qty
        laptop.save()
        return Response({'msg': 'Released successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def laptop_confirm(request, pk):
    return Response({'msg': 'Confirmed successfully'})
