# prediction/views.py - FIXED CLEAN VERSION

import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render

def index(request):
    """Serve the main frontend page"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def predict_xray_simple(request):
    """
    Prediction endpoint with LogReg integration
    """
    try:
        # Import models here to avoid import errors
        from .ml_models import get_predictor
        from .logreg_model import get_logreg_predictor
        
        # Check if image file exists
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
        
        image_file = request.FILES['image']
        city_code = request.POST.get('city', 'indonesia')
        
        # Basic validation
        if image_file.size > 10 * 1024 * 1024:  # 10MB limit
            return JsonResponse({
                'success': False,
                'error': 'File too large. Maximum 10MB allowed.'
            }, status=400)
        
        # Save uploaded image temporarily
        image_name = f"{uuid.uuid4()}_{image_file.name}"
        image_path = default_storage.save(f'temp/{image_name}', ContentFile(image_file.read()))
        full_image_path = default_storage.path(image_path)
        
        try:
            # Perform X-ray prediction
            predictor = get_predictor()
            prediction_result = predictor.predict(full_image_path)
            
            print(f"🔍 X-ray prediction: {prediction_result['classification']} ({prediction_result['confidence']:.3f})")
            
            # Get air quality data
            air_quality_data = get_country_air_quality_data(city_code)
            print(f"🌍 Country: {city_code}, AQI: {air_quality_data['aqi']}")
            
            # Get risk prediction for NORMAL cases
            risk_prediction = None
            if prediction_result['classification'].lower().strip() == 'normal':
                print(f"✅ Running LogReg for NORMAL case...")
                try:
                    logreg_predictor = get_logreg_predictor()
                    logreg_result = logreg_predictor.predict_risk(city_code)
                    
                    # Format risk prediction
                    risk_prediction = {
                        'risk_level': logreg_result['risk_level'],
                        'confidence': logreg_result['confidence'],
                        'confidence_percentage': round(logreg_result['confidence'] * 100, 1),
                        'timeline_months': logreg_result['timeline_months'],
                        'recommendations': (
                            logreg_result['recommendations']['general'] + 
                            logreg_result['recommendations']['specific']
                        )[:7],
                        'logreg_details': logreg_result
                    }
                    print(f"🎯 LogReg result: {logreg_result['risk_level']}")
                    
                except Exception as logreg_error:
                    print(f"❌ LogReg error: {logreg_error}")
                    risk_prediction = None
            
            # Clean up temporary file
            default_storage.delete(image_path)
            
            # Prepare response
            response_data = {
                'success': True,
                'classification': prediction_result['classification'],
                'confidence': prediction_result['confidence'],
                'confidence_percentage': round(prediction_result['confidence'] * 100, 1),
                'all_probabilities': prediction_result['all_probabilities'],
                'air_quality_data': air_quality_data
            }
            
            if risk_prediction:
                response_data['risk_prediction'] = risk_prediction
                print(f"📤 Sending response with risk prediction")
            
            return JsonResponse(response_data)
            
        except Exception as e:
            # Clean up temporary file if error occurs
            if default_storage.exists(image_path):
                default_storage.delete(image_path)
            raise e
            
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }, status=500)

@csrf_exempt  
@require_http_methods(["GET"])
def get_cities_simple(request):
    """Get list of countries"""
    countries = [
        {
            'code': 'indonesia', 
            'name': 'Indonesia',
            'aqi': 154,
            'description': 'Unhealthy for Sensitive Groups'
        },
        {
            'code': 'singapore', 
            'name': 'Singapore', 
            'aqi': 66,
            'description': 'Moderate'
        },
        {
            'code': 'australia', 
            'name': 'Australia',
            'aqi': 25, 
            'description': 'Good'
        }
    ]
    
    return JsonResponse({
        'success': True,
        'cities': countries
    })

@csrf_exempt
@require_http_methods(["GET"]) 
def get_air_quality_simple(request, city_code):
    """Get air quality data"""
    air_quality_data = get_country_air_quality_data(city_code)
    
    return JsonResponse({
        'success': True,
        'data': air_quality_data
    })

def get_country_air_quality_data(city_code):
    """Get air quality data for country"""
    country_data = {
        'indonesia': {
            'aqi': 154,
            'pm25': 67.92,
            'pm10': 75.52,
            'pm1': 39.60,
            'o3': 45.0,
            'no2': 31.0,
            'so2': 15.0,
            'co': 2.5,
            'humidity': 45.61,
            'temperature': 31.16,
            'country_code': 'indonesia'
        },
        'singapore': {
            'aqi': 66,
            'pm25': 20.65,
            'pm10': 22.61,
            'pm1': 13.92,
            'o3': 35.0,
            'no2': 25.0,
            'so2': 8.0,
            'co': 1.5,
            'humidity': 62.57,
            'temperature': 29.60,
            'country_code': 'singapore'
        },
        'australia': {
            'aqi': 25,
            'pm25': 5.65,
            'pm10': 6.05,
            'pm1': 4.24,
            'o3': 25.0,
            'no2': 15.0,
            'so2': 5.0,
            'co': 0.8,
            'humidity': 51.29,
            'temperature': 16.16,
            'country_code': 'australia'
        }
    }
    
    return country_data.get(city_code.lower(), country_data['indonesia'])