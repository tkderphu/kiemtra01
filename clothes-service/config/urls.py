from django.urls import path
from clothes_service import views

urlpatterns = [
    path('clothes', views.clothes_list_create),
    path('clothes/<int:pk>', views.clothes_detail),
    path('health/', views.health_check),
]
