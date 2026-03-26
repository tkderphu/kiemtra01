import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from clothes_service.models import Clothes

if not Clothes.objects.exists():
    Clothes.objects.create(name='Áo thun T-Shirt basic', price=20)
    Clothes.objects.create(name='Quần Jeans nam', price=40)
    Clothes.objects.create(name='Áo khoác sơ mi', price=35)
    Clothes.objects.create(name='Áo Hoodies mùa đông', price=55)
    print("Seeded Clothes")
