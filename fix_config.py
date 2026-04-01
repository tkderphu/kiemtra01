import os

services_apps = {
    'order-service': ('order_service', 'order_db'),
    'payment-service': ('payment_service', 'payment_db'),
    'shipping-service': ('shipping_service', 'shipping_db'),
    'comment-rate-service': ('comment_rate_service', 'comment_db')
}

settings_tpl = """import os
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
    '{app}',
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
        'NAME': os.environ.get('DB_NAME', '{db}'),
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
"""

wsgi_tpl = """import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
"""

for svc, (app, db) in services_apps.items():
    s_path = f"{svc}/config/settings.py"
    with open(s_path, 'w') as f:
        f.write(settings_tpl.format(app=app, db=db))
        
    w_path = f"{svc}/config/wsgi.py"
    with open(w_path, 'w') as f:
        f.write(wsgi_tpl)
        
    i_path = f"{svc}/config/__init__.py"
    with open(i_path, 'w') as f:
        f.write("")
        
    i2_path = f"{svc}/{app}/__init__.py"
    with open(i2_path, 'w') as f:
        f.write("")

print("Config files generated successfully.")
