from django.urls import path
from tracking_service import views

urlpatterns = [
    path('health/', views.health_check),
    path('track', views.track_event),

]
