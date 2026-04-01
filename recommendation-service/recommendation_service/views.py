import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Interaction
from django.db.models import Sum
from .ml_model import get_ml_recommendations

def health_check(request):
    return JsonResponse({'status': 'recommend ok'})

@csrf_exempt
def get_recommendations(request, user_id):
    if request.method == 'GET':
        try:
            # Sử dụng Machine Learning Model (SVD Matrix Factorization)
            recommended_ids = get_ml_recommendations(user_id)

            return JsonResponse({'user_id': user_id, 'recommended_product_ids': recommended_ids, 'algorithm': 'Matrix Factorization (SVD)'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
