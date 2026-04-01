from django.urls import path
from clothes_service import views

urlpatterns = [
    path('clothes', views.clothes_list_create),
    path('clothes/count', views.clothes_count),
    path('clothes/<int:pk>', views.clothes_detail),
    path('clothes/<int:pk>/reserve', views.clothes_reserve),
    path('clothes/<int:pk>/release', views.clothes_release),
    path('clothes/<int:pk>/confirm', views.clothes_confirm),
    path('health/', views.health_check),
]
