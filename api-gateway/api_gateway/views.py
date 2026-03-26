import os
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

STAFF_URL = os.environ.get('STAFF_SERVICE_URL', 'http://staff-service:8000')
CUSTOMER_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:8000')
CART_URL = os.environ.get('CART_SERVICE_URL', 'http://cart-service:8000')
LAPTOP_URL = os.environ.get('LAPTOP_SERVICE_URL', 'http://laptop-service:8000')
CLOTHES_URL = os.environ.get('CLOTHES_SERVICE_URL', 'http://clothes-service:8000')

def health_check(request):
    return JsonResponse({'status': 'gateway ok'})

def staff_ui(request):
    return render(request, 'staff.html')

def customer_ui(request):
    return render(request, 'customer.html')

@csrf_exempt
def proxy_request(request, path):
    url_map = {
        'staff/': STAFF_URL,
        'customer/': CUSTOMER_URL,
        'cart/': CART_URL,
        'laptops/': LAPTOP_URL,
        'clothes/': CLOTHES_URL,
        'staff': STAFF_URL,
        'customer': CUSTOMER_URL,
        'cart': CART_URL,
        'laptops': LAPTOP_URL,
        'clothes': CLOTHES_URL,
    }
    
    target_base = None
    # Fix: Ensure precise matching logic so "staff-ui" doesn't falsely match "staff" prefix.
    # By strictly matching full paths or paths starting with 'prefix/'
    for prefix, base in url_map.items():
        if path == prefix.strip('/') or path.startswith(prefix if prefix.endswith('/') else prefix + '/'):
            target_base = base
            break
            
    if not target_base:
        return JsonResponse({'error': 'Service Route Not Found', 'path': path}, status=404)
        
    target_url = f"{target_base}/{path}"
    
    try:
        headers = {}
        if request.content_type:
            headers['Content-Type'] = request.content_type
            
        if request.method == 'GET':
            resp = requests.get(target_url, params=request.GET, headers=headers)
        elif request.method == 'POST':
            resp = requests.post(target_url, data=request.body, headers=headers)
        elif request.method == 'PUT':
            resp = requests.put(target_url, data=request.body, headers=headers)
        elif request.method == 'DELETE':
            resp = requests.delete(target_url, headers=headers)
        else:
            return JsonResponse({'error': 'Method not supported'}, status=405)
            
        return HttpResponse(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
    except Exception as e:
        return JsonResponse({'error': str(e), 'target': target_url}, status=500)
