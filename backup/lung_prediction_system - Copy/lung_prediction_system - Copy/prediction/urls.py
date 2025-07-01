from django.urls import path
from . import views

urlpatterns = [
    # Frontend page
    path('', views.index, name='index'),
    
    # Simple API endpoints untuk testing
    path('api/predict/', views.predict_xray_simple, name='predict_simple'),
    path('api/cities/', views.get_cities_simple, name='cities_simple'),
    path('api/air-quality/<str:city_code>/', views.get_air_quality_simple, name='air_quality_simple'),
]