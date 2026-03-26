import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from staff_service.models import Staff

if not Staff.objects.exists():
    Staff.objects.create(username='admin', password='admin')
    Staff.objects.create(username='staff1', password='password123')
    print("Seeded Staff")
