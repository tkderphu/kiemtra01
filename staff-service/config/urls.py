from django.urls import path
from staff_service import views

urlpatterns = [
    path('staff/login', views.login),
    path('health/', views.health_check),
]
