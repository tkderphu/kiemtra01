import json
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
