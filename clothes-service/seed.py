import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE clothes_service_clothes ADD COLUMN IF NOT EXISTS brand VARCHAR(100) DEFAULT 'Unknown';")
        cursor.execute("ALTER TABLE clothes_service_clothes ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);")
        cursor.execute("ALTER TABLE clothes_service_clothes ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 10;")
except Exception as e:
    print("SQL Patch error or already exists:", e)

from clothes_service.models import Clothes

# Wipe old data to ensure new beautiful mock data is applied
Clothes.objects.all().delete()

Clothes.objects.create(name='Áo thun Cotton', brand='Uniqlo', price=300.00, image_url='https://bizweb.dktcdn.net/100/438/408/products/1-fbbb2da4-4c8d-4a16-95f3-5290b23f2f89.jpg?v=1686903337920')
Clothes.objects.create(name='Quần Jeans Slimf', brand='Levis', price=800.00, image_url='https://img.lazcdn.com/g/p/920211be17efaa0318683e336e84d9af.jpg_720x720q80.jpg')
Clothes.objects.create(name='Áo khoác dù', brand='Adidas', price=1200.00, image_url='https://assets.adidas.com/images/h_840,f_auto,q_auto,fl_lossy,c_fill,g_auto/09c5ea6df1bd4be6baaaac5e003e7047_9366/Ao_Khoac_Tiro_21_Djen_GH4462_21_model.jpg')
Clothes.objects.create(name='Áo sơ mi dài tay', brand='Zara', price=500.00, image_url='https://static.zara.net/photos///2024/V/0/2/p/3057/061/250/2/w/400/3057061250_6_1_1.jpg')
print("Seeded Clothes successfully")
