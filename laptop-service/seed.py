import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE laptop_service_laptop ADD COLUMN IF NOT EXISTS brand VARCHAR(100) DEFAULT 'Unknown';")
        cursor.execute("ALTER TABLE laptop_service_laptop ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);")
        cursor.execute("ALTER TABLE laptop_service_laptop ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 10;")
except Exception as e:
    print("SQL Patch error or already exists:", e)

from laptop_service.models import Laptop

# Wipe old data to ensure new beautiful mock data is applied
Laptop.objects.all().delete()

Laptop.objects.create(name='MacBook Pro M2 13-inch', brand='Apple', price=30000.00, image_url='https://cdn.tgdd.vn/Products/Images/44/282827/apple-macbook-pro-13-inch-m2-2022-xam-600x600.jpg')
Laptop.objects.create(name='Asus ROG Strix G15', brand='Asus', price=25000.00, image_url='https://cdn.tgdd.vn/Products/Images/44/304711/asus-tuf-gaming-f15-fx506hf-i5-hn014w-glr-2-600x600.jpg')
Laptop.objects.create(name='HP Pavilion 14', brand='HP', price=15000.00, image_url='https://cdn.tgdd.vn/Products/Images/44/302028/hp-pavilion-15-eg2056tu-i5-6k786pa-glr-2-600x600.jpg')
Laptop.objects.create(name='Dell XPS 13 Plus', brand='Dell', price=35000.00, image_url='https://cdn.tgdd.vn/Products/Images/44/281146/dell-xps-13-plus-9320-i7-5g168w-glr-2-600x600.jpg')
print("Seeded Laptops successfully")
