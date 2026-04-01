import os

services_apps = {
    'order-service': 'order_service',
    'payment-service': 'payment_service',
    'shipping-service': 'shipping_service',
    'comment-rate-service': 'comment_rate_service'
}

reqs = "Django>=4.0\npsycopg2-binary\ndjangorestframework\ncorsheaders\nrequests\n"

manage_py = """#!/usr/bin/env python
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
"""

for svc, app in services_apps.items():
    with open(f"{svc}/requirements.txt", "w") as f: 
        f.write(reqs)
    with open(f"{svc}/manage.py", "w") as f: 
        f.write(manage_py)
    dockerfile = f"""FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "python manage.py makemigrations {app} && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
"""
    with open(f"{svc}/Dockerfile", "w") as f: 
        f.write(dockerfile)

print("Created Dockerfile, manage.py, requirements.txt for all 4 services!")
