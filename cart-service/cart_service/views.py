from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .models import Cart, CartItem

def health_check(request):
    return JsonResponse({'status': 'cart service ok'})

@api_view(['POST'])
def add_cart(request):
    data = json.loads(request.body)
    customer_id = data.get('customer_id')
    product_id = data.get('product_id')
    qty = data.get('qty', 1)
    
    if not customer_id or not product_id:
        return Response({'error': 'customer_id and product_id required'}, status=400)
        
    cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
    item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
    if not created:
        item.qty += qty
        item.save()
    else:
        item.qty = qty
        item.save()
        
    return Response({'msg': 'Product added to cart', 'cart_id': cart.id})

@api_view(['GET'])
def get_cart(request, customer_id):
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        items = [i.to_dict() for i in cart.items.all()]
        return Response({'customer_id': customer_id, 'cart_id': cart.id, 'items': items})
    except Cart.DoesNotExist:
        return Response({'customer_id': customer_id, 'items': []})
