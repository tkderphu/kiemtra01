import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from laptop_service.models import Laptop

if not Laptop.objects.exists():
    Laptop.objects.create(name='MacBook Pro M2', price=1500)
    Laptop.objects.create(name='Dell XPS 13', price=1200)
    Laptop.objects.create(name='ThinkPad T14', price=1100)
    Laptop.objects.create(name='Asus ROG Zephyrus', price=1800)
    print("Seeded Laptops")
