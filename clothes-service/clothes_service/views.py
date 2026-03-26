from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .models import Clothes

def health_check(request):
    return JsonResponse({'status': 'clothes service ok'})

@api_view(['GET', 'POST'])
def clothes_list_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        c = Clothes.objects.create(name=data.get('name', 'Unknown'), price=data.get('price', 0))
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
        c.price = data.get('price', c.price)
        c.save()
        return Response({'msg': f'Clothes {pk} updated', 'clothes': c.to_dict()})
        
    c.delete()
    return Response({'msg': f'Clothes {pk} deleted'})
