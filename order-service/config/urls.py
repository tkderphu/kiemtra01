from django.urls import path
from order_service import views

urlpatterns = [
    path('health/', views.health_check),
    path('orders', views.orders_list_create),
    path('orders/payment-callback', views.payment_callback),
    path('orders/shipping-callback', views.shipping_callback),
    path('orders/<str:pk>', views.order_detail),
]
