import os

def scaffold_django_app(service, app_name, db_name=None, extra_reqs="", extra_settings="", extra_views="", extra_urls="", management_command=None):
    os.makedirs(f'{service}/{app_name}', exist_ok=True)
    os.makedirs(f'{service}/config', exist_ok=True)

    cmd = f'python manage.py makemigrations {app_name} && python manage.py migrate && python seed.py && ' if db_name else ''
    
    # Dockerfile
    with open(f'{service}/Dockerfile', 'w') as f:
        f.write(f'''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "{cmd}python manage.py runserver 0.0.0.0:8000"]
''')

    # requirements.txt
    with open(f'{service}/requirements.txt', 'w') as f:
        f.write(f'Django>=4.0\nrestframework\ncorsheaders\nrequests\nkafka-python\n{extra_reqs}\n')

    # manage.py
    with open(f'{service}/manage.py', 'w') as f:
        f.write('''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
''')

    # settings.py
    db_config = f'''DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', '{db_name}'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'rootpassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }}
}}''' if db_name else 'DATABASES = {}'

    with open(f'{service}/config/settings.py', 'w') as f:
        f.write(f'''import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'corsheaders',
    '{app_name}',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

{db_config}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True

{extra_settings}
''')

    # urls.py
    with open(f'{service}/config/urls.py', 'w') as f:
        f.write(f'''from django.urls import path
from {app_name} import views

urlpatterns = [
    path('health/', views.health_check),
{extra_urls}
]
''')

    # wsgi.py
    with open(f'{service}/config/wsgi.py', 'w') as f:
        f.write('''import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
''')

    # empty inits
    open(f'{service}/config/__init__.py', 'w').close()
    open(f'{service}/{app_name}/__init__.py', 'w').close()

    # seed if db
    if db_name:
        with open(f'{service}/seed.py', 'w') as f:
            f.write('''import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("Seeded successfully")
''')

    if management_command:
        d = f'{service}/{app_name}/management/commands'
        os.makedirs(d, exist_ok=True)
        open(f'{service}/{app_name}/management/__init__.py', 'w').close()
        open(f'{d}/__init__.py', 'w').close()
        for k, v in management_command.items():
            with open(f'{d}/{k}.py', 'w') as f:
                f.write(v)


# ---------------- TRACKING SERVICE ----------------
tracking_views = '''import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from kafka import KafkaProducer
import os

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')

def get_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
    except Exception as e:
        print("Kafka Producer Init Failed:", e)
        return None

producer = get_producer()

def health_check(request):
    return JsonResponse({'status': 'tracking ok'})

@csrf_exempt
def track_event(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # data: {user_id, product_id, action}
            user_id = data.get('user_id')
            product_id = data.get('product_id')
            action = data.get('action') # VIEW, ADD_CART, PURCHASE
            
            if not all([user_id, product_id, action]):
                return JsonResponse({'error': 'Missing fields'}, status=400)
            
            weight = 1
            if action == 'ADD_CART': weight = 3
            if action == 'PURCHASE': weight = 5
            
            payload = {
                'user_id': user_id,
                'product_id': product_id,
                'action': action,
                'weight': weight
            }
            
            global producer
            if not producer: producer = get_producer()
            
            if producer:
                producer.send('user-interactions', value=payload)
                producer.flush()
                return JsonResponse({'status': 'Event tracked', 'event': payload}, status=201)
            else:
                return JsonResponse({'error': 'Kafka unavailable but tracking received'}, status=202)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
'''

with open('scaffold_tracking.py', 'w') as f: pass # dummy

scaffold_django_app(
    service='tracking-service',
    app_name='tracking_service',
    db_name=None, # no db needed
    extra_reqs="",
    extra_urls="    path('track', views.track_event),\n"
)
with open('tracking-service/tracking_service/views.py', 'w') as f: f.write(tracking_views)

# ---------------- RECOMMENDATION SERVICE ----------------
recommend_views = '''import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Interaction
from django.db.models import Sum

def health_check(request):
    return JsonResponse({'status': 'recommend ok'})

@csrf_exempt
def get_recommendations(request, user_id):
    if request.method == 'GET':
        try:
            # Simple ML Heuristic: 
            # 1. Find the user's top weighted products
            user_top = Interaction.objects.filter(user_id=user_id).values('product_id').annotate(total_score=Sum('weight')).order_by('-total_score')[:5]
            user_product_ids = [item['product_id'] for item in user_top]
            
            # 2. If user has no history, just return globally popular products
            if not user_product_ids:
                global_top = Interaction.objects.values('product_id').annotate(total_score=Sum('weight')).order_by('-total_score')[:10]
                recommended_ids = [item['product_id'] for item in global_top]
            else:
                # 3. Simple Collaborative Logic: Users who interacted with user's top products also interacted with...
                similar_users = Interaction.objects.filter(product_id__in=user_product_ids).exclude(user_id=user_id).values_list('user_id', flat=True).distinct()
                
                # Products they interacted with, sorted by total weight
                similar_products = Interaction.objects.filter(user_id__in=similar_users).exclude(product_id__in=user_product_ids)
                scored_products = similar_products.values('product_id').annotate(total_score=Sum('weight')).order_by('-total_score')[:10]
                
                recommended_ids = [item['product_id'] for item in scored_products]
                
                # Fallback if no similar users found
                if not recommended_ids:
                    global_top = Interaction.objects.exclude(product_id__in=user_product_ids).values('product_id').annotate(total_score=Sum('weight')).order_by('-total_score')[:10]
                    recommended_ids = [item['product_id'] for item in global_top]

            # In a real-world scenario, we would join this with product details. 
            # Our frontend UI can resolve the product_ids to names.
            return JsonResponse({'user_id': user_id, 'recommended_product_ids': recommended_ids}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
'''

consume_cmd = '''import json
import os
import time
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from recommendation_service.models import Interaction

class Command(BaseCommand):
    help = 'Starts the Kafka Consumer for user-interactions'

    def handle(self, *args, **options):
        broker = os.environ.get('KAFKA_BROKER', 'kafka:9092')
        self.stdout.write(f"Connecting to Kafka broker: {broker}")
        
        consumer = None
        for i in range(10):
            try:
                consumer = KafkaConsumer(
                    'user-interactions',
                    bootstrap_servers=[broker],
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    group_id='recommendation-group',
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
                self.stdout.write("Kafka Consumer connected successfully!")
                break
            except Exception as e:
                self.stdout.write(f"Failed to connect (attempt {i+1}/10): {e}. Retrying in 5s...")
                time.sleep(5)
                
        if not consumer:
            self.stdout.write("Could not connect to Kafka. Exiting consumer.")
            return

        self.stdout.write("Listening for events on 'user-interactions' topic...")
        for message in consumer:
            event = message.value
            self.stdout.write(f"Received event: {event}")
            try:
                Interaction.objects.create(
                    user_id=event.get('user_id'),
                    product_id=event.get('product_id'),
                    action=event.get('action'),
                    weight=event.get('weight', 1)
                )
            except Exception as e:
                self.stdout.write(f"Error saving event to DB: {e}")
'''

scaffold_django_app(
    service='recommendation-service',
    app_name='recommendation_service',
    db_name='recommend_db',
    extra_reqs="psycopg2-binary\n",
    extra_urls="    path('recommend/<int:user_id>', views.get_recommendations),\n",
    management_command={'run_kafka_consumer': consume_cmd}
)

# Fix Recommendation Dockerfile to run the consumer in background!
with open('recommendation-service/Dockerfile', 'w') as f:
    f.write('''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Start the Django server and run the kafka consumer in the background
CMD ["sh", "-c", "python manage.py makemigrations recommendation_service && python manage.py migrate && python seed.py && python manage.py run_kafka_consumer & python manage.py runserver 0.0.0.0:8000"]
''')

with open('recommendation-service/recommendation_service/models.py', 'w') as f:
    f.write('''from django.db import models

class Interaction(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    action = models.CharField(max_length=50) # VIEW, ADD_CART, PURCHASE
    weight = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
''')

with open('recommendation-service/recommendation_service/views.py', 'w') as f: f.write(recommend_views)

print("Tracking and Recommendation Kafka services scaffolded successfully!")
