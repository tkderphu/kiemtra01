import os
import sys

SERVICES = [
    "api-gateway",
    "staff-service",
    "customer-service",
    "cart-service",
    "laptop-service",
    "clothes-service"
]

MANAGE_PY = """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""

SETTINGS_PY = """
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-test-key-replace-in-prod'
DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    '{service_app}',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')] if "{service_app}" == "api_gateway" else [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True

{db_config}
"""

DB_CONFIG_MYSQL = """
# Override default with MySQL if env vars exist
DB_NAME = os.environ.get('DB_NAME')
if DB_NAME:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'rootpassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
"""

DB_CONFIG_POSTGRES = """
# Override default with Postgres if env vars exist
DB_NAME = os.environ.get('DB_NAME')
if DB_NAME:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'rootpassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
"""

URLS_PY = """
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('{service_app}.urls')),
]
"""

APP_APPS_PY = """
from django.apps import AppConfig

class {app_camel}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{service_app}'
"""

APP_URLS_PY = """
from django.urls import path
from . import views

urlpatterns = [
    # To be implemented
]
"""

APP_VIEWS_PY = """
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok'})
"""

for service in SERVICES:
    app_name = service.replace("-", "_")
    
    # determines db config to append
    db_config_code = ""
    if "mysql" in open(f"{service}/Dockerfile").read() or "mysql" in open(f"{service}/requirements.txt").read():
        db_config_code = DB_CONFIG_MYSQL
    elif "psycopg2" in open(f"{service}/requirements.txt").read():
        db_config_code = DB_CONFIG_POSTGRES
    elif service == "api-gateway":
        pass # default sqlite is fine
        
    os.makedirs(f"{service}/config", exist_ok=True)
    os.makedirs(f"{service}/{app_name}", exist_ok=True)
    
    # write manage.py
    with open(f"{service}/manage.py", "w") as f:
        f.write(MANAGE_PY)
        
    # write config/__init__.py
    with open(f"{service}/config/__init__.py", "w") as f:
        f.write("")
        
    # write config/settings.py
    with open(f"{service}/config/settings.py", "w") as f:
        f.write(SETTINGS_PY.format(service_app=app_name, db_config=db_config_code))
        
    # write config/urls.py
    with open(f"{service}/config/urls.py", "w") as f:
        f.write(URLS_PY.format(service_app=app_name))
        
    # write app/__init__.py
    with open(f"{service}/{app_name}/__init__.py", "w") as f:
        f.write("")
        
    # write app/apps.py
    app_camel = "".join(x.capitalize() for x in app_name.split("_"))
    with open(f"{service}/{app_name}/apps.py", "w") as f:
        f.write(APP_APPS_PY.format(app_camel=app_camel, service_app=app_name))
        
    # write app/urls.py
    with open(f"{service}/{app_name}/urls.py", "w") as f:
        f.write(APP_URLS_PY)
        
    # write app/views.py
    with open(f"{service}/{app_name}/views.py", "w") as f:
        f.write(APP_VIEWS_PY)

print("Django boilerplate generated successfully.")
