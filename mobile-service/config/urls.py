from django.contrib import admin
from django.urls import path, include
from mobile_service import views

urlpatterns = [
    path('mobiles', views.mobile_list_create),
    path('mobiles/count', views.mobile_count),
    path('mobiles/<int:pk>', views.mobile_detail),
    path('mobiles/<int:pk>/reserve', views.mobile_reserve),
    path('mobiles/<int:pk>/release', views.mobile_release),
    path('mobiles/<int:pk>/confirm', views.mobile_confirm),
    path('health/', views.health_check),
]
