from django.urls import path
from laptop_service import views

urlpatterns = [
    path('laptops', views.laptop_list_create),
    path('laptops/count', views.laptop_count),
    path('laptops/<int:pk>', views.laptop_detail),
    path('laptops/<int:pk>/reserve', views.laptop_reserve),
    path('laptops/<int:pk>/release', views.laptop_release),
    path('laptops/<int:pk>/confirm', views.laptop_confirm),
    path('health/', views.health_check),
]
