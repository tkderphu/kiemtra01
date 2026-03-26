import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from customer_service.models import Customer

if not Customer.objects.exists():
    # user matches the default login credentials in UI
    Customer.objects.create(username='user', password='pass')
    Customer.objects.create(username='khachhang1', password='123')
    print("Seeded Customer")
