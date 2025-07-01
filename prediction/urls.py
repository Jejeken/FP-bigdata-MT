# prediction/urls.py - FIXED TO MATCH FRONTEND
from django.urls import path
from . import views

urlpatterns = [
    # Frontend page
    path('', views.index, name='index'),
    
    # FIXED: Match frontend expectations (prediction/ is added by main URLs)
    path('prediction/cities/', views.get_cities_simple, name='cities_simple'),
    path('prediction/air-quality/<str:city_code>/', views.get_air_quality_simple, name='air_quality_simple'),
    path('prediction/predict/', views.predict_xray_simple, name='predict_simple'),
    
    # Keep API endpoints for backward compatibility
    path('api/predict/', views.predict_xray_simple, name='api_predict_simple'),
    path('api/cities/', views.get_cities_simple, name='api_cities_simple'),
    path('api/air-quality/<str:city_code>/', views.get_air_quality_simple, name='api_air_quality_simple'),
]