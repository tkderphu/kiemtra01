from django.urls import path, re_path
from api_gateway import views

urlpatterns = [
    path('staff-ui/', views.staff_ui),
    path('staff-ui', views.staff_ui),
    path('customer-ui/', views.customer_ui),
    path('customer-ui', views.customer_ui),
    path('health/', views.health_check),
    path('health', views.health_check),
    re_path(r'^(?P<path>.*)$', views.proxy_request),
]
