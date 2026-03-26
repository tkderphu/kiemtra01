from django.urls import path
from customer_service import views

urlpatterns = [
    path('customer/register', views.register),
    path('customer/login', views.login),
    path('health/', views.health_check),
]
