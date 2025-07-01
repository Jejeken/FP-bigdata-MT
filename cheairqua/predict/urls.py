from django.urls import path
from . import views


app_name = 'predict'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/air-quality/<int:location_id>/', views.air_quality_api, name='air_quality_api'),
]