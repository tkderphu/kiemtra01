import os

service = 'comment-rate-service'
app_name = 'comment_rate_service'
db_name = 'comment_db'

os.makedirs(f'{service}/{app_name}', exist_ok=True)
os.makedirs(f'{service}/config', exist_ok=True)

# Dockerfile
with open(f'{service}/Dockerfile', 'w') as f:
    f.write(f'''FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "python manage.py makemigrations {app_name} && python manage.py migrate && python seed.py && python manage.py runserver 0.0.0.0:8000"]
''')

# requirements.txt
with open(f'{service}/requirements.txt', 'w') as f:
    f.write('Django>=4.0\npsycopg2-binary\ndjangorestframework\ncorsheaders\nrequests\n')

# manage.py
with open(f'{service}/manage.py', 'w') as f:
    f.write(f'''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
''')

# settings.py
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
    'rest_framework',
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

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', '{db_name}'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'rootpassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }}
}}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True
''')

# urls.py
with open(f'{service}/config/urls.py', 'w') as f:
    f.write(f'''from django.urls import path
from {app_name} import views

urlpatterns = [
    path('health/', views.health_check),
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

# seed.py
with open(f'{service}/seed.py', 'w') as f:
    f.write('''import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("Seeded successfully")
''')

print("Comment service scaffolded!")
