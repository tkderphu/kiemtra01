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
ORDER_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8000')
PAYMENT_URL = os.environ.get('PAYMENT_SERVICE_URL', 'http://payment-service:8000')
SHIPPING_URL = os.environ.get('SHIPPING_SERVICE_URL', 'http://shipping-service:8000')
COMMENT_URL = os.environ.get('COMMENT_SERVICE_URL', 'http://comment-rate-service:8000')
TRACK_URL = os.environ.get('TRACKING_SERVICE_URL', 'http://tracking-service:8000')
RECOMMEND_URL = os.environ.get('RECOMMEND_SERVICE_URL', 'http://recommendation-service:8000')
MOBILE_URL = os.environ.get('MOBILE_SERVICE_URL', 'http://mobile-service:8000')
BEHAVIOR_URL = os.environ.get('BEHAVIOR_SERVICE_URL', 'http://ai_behavior:8001')
KB_URL = os.environ.get('KB_SERVICE_URL', 'http://ai_kb:8002')
CHATBOT_URL = os.environ.get('CHATBOT_SERVICE_URL', 'http://ai_chatbot:8003')

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
        'orders/': ORDER_URL,
        'payments/': PAYMENT_URL,
        'shipments/': SHIPPING_URL,
        'comments/': COMMENT_URL,
        'track/': TRACK_URL,
        'recommend/': RECOMMEND_URL,
        'mobiles/': MOBILE_URL,
        'staff': STAFF_URL,
        'customer': CUSTOMER_URL,
        'cart': CART_URL,
        'laptops': LAPTOP_URL,
        'clothes': CLOTHES_URL,
        'orders': ORDER_URL,
        'payments': PAYMENT_URL,
        'shipments': SHIPPING_URL,
        'comments': COMMENT_URL,
        'track': TRACK_URL,
        'recommend': RECOMMEND_URL,
        'mobiles': MOBILE_URL,
        'analyze/': BEHAVIOR_URL,
        'analyze': BEHAVIOR_URL,
        'rebuild/': KB_URL,
        'rebuild': KB_URL,
        'chat/': CHATBOT_URL,
        'chat': CHATBOT_URL,
        'ai/analyze/': BEHAVIOR_URL,
        'ai/analyze': BEHAVIOR_URL,
        'ai/kb/': KB_URL,
        'ai/kb': KB_URL,
        'ai/chat/': CHATBOT_URL,
        'ai/chat': CHATBOT_URL,
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
