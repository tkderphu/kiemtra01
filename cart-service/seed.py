import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from cart_service.models import Cart, CartItem

if not Cart.objects.exists():
    # customer_id=1 relates to 'user' in customer database
    cart = Cart.objects.create(customer_id=1)
    CartItem.objects.create(cart=cart, product_id=1, qty=1)
    CartItem.objects.create(cart=cart, product_id=2, qty=2)
    print("Seeded Cart")
