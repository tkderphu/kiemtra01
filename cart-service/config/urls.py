from django.urls import path
from cart_service import views

urlpatterns = [
    path('cart/add', views.add_cart),
    path('cart/<int:customer_id>', views.get_cart),
    path('health/', views.health_check),
]
