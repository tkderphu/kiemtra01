from django.urls import path
from recommendation_service import views

urlpatterns = [
    path('health/', views.health_check),
    path('recommend/<int:user_id>', views.get_recommendations),

]
