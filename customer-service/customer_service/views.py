from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .models import Customer

def health_check(request):
    return JsonResponse({'status': 'customer service ok'})

@api_view(['POST'])
def register(request):
    data = json.loads(request.body) if request.body else {}
    username = data.get('username', 'user')
    pw = data.get('password', 'pass')
    if Customer.objects.filter(username=username).exists():
        return Response({'error': 'Username exists'}, status=400)
    Customer.objects.create(username=username, password=pw)
    return Response({'msg': 'Customer registered successfully'})

@api_view(['POST'])
def login(request):
    data = json.loads(request.body) if request.body else {}
    username = data.get('username', 'user')
    pw = data.get('password', 'pass')
    
    if not Customer.objects.exists():
        c = Customer.objects.create(username=username, password=pw)
    else:
        c = Customer.objects.filter(username=username, password=pw).first()
        if not c:
            return Response({'error': 'Invalid credentials'}, status=401)
            
    return Response({'token': 'customer-jwt-token', 'customer_id': c.id, 'msg': 'Login successful'})
