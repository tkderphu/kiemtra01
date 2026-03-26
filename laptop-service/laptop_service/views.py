from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .models import Laptop

def health_check(request):
    return JsonResponse({'status': 'laptop service ok'})

@api_view(['GET', 'POST'])
def laptop_list_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        laptop = Laptop.objects.create(name=data.get('name', 'Unknown'), price=data.get('price', 0))
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
        laptop.price = data.get('price', laptop.price)
        laptop.save()
        return Response({'msg': f'Laptop {pk} updated', 'laptop': laptop.to_dict()})
        
    laptop.delete()
    return Response({'msg': f'Laptop {pk} deleted'})
