from django.urls import path
from payment_service import views

urlpatterns = [
    path('health/', views.health_check),
    path('payments', views.create_payment),
    path('payments/callback', views.payment_gateway_callback),
]
