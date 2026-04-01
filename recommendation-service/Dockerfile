FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Start the Django server and run the kafka consumer in the background
CMD ["sh", "-c", "python manage.py makemigrations recommendation_service && python manage.py migrate && python seed.py && python manage.py run_kafka_consumer & python manage.py runserver 0.0.0.0:8000"]
