import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Comment

ORDER_SERVICE_URL = "http://order-service:8000"

def health_check(request):
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def get_comments(request, product_type, product_id):
    if request.method == 'GET':
        comments = Comment.objects.filter(product_type=product_type, product_id=product_id).order_by('-created_at')
        
        # Calculate average rating
        total_rating = sum(c.rating for c in comments)
        avg_rating = total_rating / len(comments) if len(comments) > 0 else 0
        
        return JsonResponse({
            'average_rating': round(avg_rating, 1),
            'total_comments': len(comments),
            'comments': [c.to_dict() for c in comments]
        })

@csrf_exempt
def create_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            product_id = data.get('product_id')
            product_type = data.get('product_type')
            content = data.get('content')
            rating = data.get('rating')

            if not all([user_id, product_id, product_type, content, rating]):
                return JsonResponse({'error': 'Missing fields'}, status=400)

            # --- Business Logic: Verify user bought this item ---
            try:
                resp = requests.get(f"{ORDER_SERVICE_URL}/orders", timeout=5)
                if resp.status_code == 200:
                    orders = resp.json()
                    has_bought = False
                    for order in orders:
                        if str(order.get('customer_id')) == str(user_id) and order.get('status') == 'COMPLETED':
                            for item in order.get('items', []):
                                if str(item.get('product_id')) == str(product_id) and item.get('product_type') == product_type:
                                    has_bought = True
                                    break
                    
                    if not has_bought:
                        return JsonResponse({'error': 'Bạn cần mua sản phẩm này và đơn hàng phải được giao thành công (COMPLETED) để đánh giá.'}, status=403)
            except Exception as e:
                print("Failed to verify order status:", e)
                return JsonResponse({'error': 'Failed to verify purchase status. Try again later.'}, status=500)

            # Create comment
            comment = Comment.objects.create(
                user_id=int(user_id),
                product_id=int(product_id),
                product_type=product_type,
                content=content,
                rating=int(rating)
            )
            return JsonResponse(comment.to_dict(), status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
