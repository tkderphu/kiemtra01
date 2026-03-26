from django.urls import path
from laptop_service import views

urlpatterns = [
    path('laptops', views.laptop_list_create),
    path('laptops/count', views.laptop_count),
    path('laptops/<int:pk>', views.laptop_detail),
    path('health/', views.health_check),
]
