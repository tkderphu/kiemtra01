from django.urls import path
from comment_rate_service import views

urlpatterns = [
    path('health/', views.health_check),
    path('comments', views.create_comment),
    path('comments/<str:product_type>/<int:product_id>', views.get_comments),
]
