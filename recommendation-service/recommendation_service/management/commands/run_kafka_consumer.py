import json
import os
import time
from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
from recommendation_service.models import Interaction
from recommendation_service.ml_model import train_model

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

        event_counter = 0

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
                
                # Background Retraining Logic: 
                # Retrain after every 3 new interactions (for demonstration speed)
                event_counter += 1
                if event_counter >= 3:
                    self.stdout.write("Triggering Background ML Retraining...")
                    train_model()
                    event_counter = 0

            except Exception as e:
                self.stdout.write(f"Error saving event to DB: {e}")
