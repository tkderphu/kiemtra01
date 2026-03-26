from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .models import Staff

def health_check(request):
    return JsonResponse({'status': 'staff service ok'})

@api_view(['POST'])
def login(request):
    data = json.loads(request.body) if request.body else {}
    username = data.get('username', 'admin')
    pw = data.get('password', 'admin')
    
    if not Staff.objects.exists():
        Staff.objects.create(username=username, password=pw)
        
    if Staff.objects.filter(username=username, password=pw).exists():
        return Response({'token': 'staff-jwt-token', 'msg': 'Login successful'})
    return Response({'error': 'Invalid credentials'}, status=401)
