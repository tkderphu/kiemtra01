from django.urls import path
from shipping_service import views

urlpatterns = [
    path('health/', views.health_check),
    path('shipments', views.shipments_list_create),
    path('shipments/<str:pk>/status', views.shipment_update_status),
]
