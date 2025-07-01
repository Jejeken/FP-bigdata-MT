# prediction/views.py - ENHANCED VERSION WITH REAL-TIME AQI WEIGHTING
# Update the predict_xray_simple function with enhanced risk prediction

import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
import logging

# ENHANCED: Import enhanced risk prediction
from .enhanced_risk_prediction import enhanced_risk_prediction

logger = logging.getLogger(__name__)

def index(request):
    """Serve the main frontend page"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def predict_xray_simple(request):
    """
    ENHANCED: Main prediction endpoint dengan Real-time AQI weighted risk prediction
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
            
            logger.info(f"🔍 X-ray prediction: {prediction_result['classification']} ({prediction_result['confidence']:.3f})")
            
            # Get real-time air quality data
            air_quality_data = get_country_air_quality_data(city_code)
            aqi_value = air_quality_data.get('aqi', 'N/A')
            data_source = air_quality_data.get('data_source', 'unknown')
            
            logger.info(f"🌍 Real-time air quality: AQI={aqi_value}, Source={data_source}")
            
            # ENHANCED: Get risk prediction for NORMAL cases with AQI weighting
            enhanced_risk_prediction_result = None
            if prediction_result['classification'].lower().strip() == 'normal':
                logger.info(f"✅ Running ENHANCED risk prediction for NORMAL case...")
                try:
                    # Get original LogReg prediction
                    logreg_predictor = get_logreg_predictor()
                    original_logreg_result = logreg_predictor.predict_risk(city_code)
                    
                    logger.info(f"🤖 Original LogReg result: {original_logreg_result['risk_level']}")
                    logger.info(f"🌍 Real-time AQI for enhancement: {aqi_value}")
                    
                    # ENHANCED: Apply real-time AQI weighting
                    enhanced_result = enhanced_risk_prediction(
                        logreg_result=original_logreg_result,
                        air_quality_data=air_quality_data,
                        aqi_weight=0.85  # 85% weight for AQI, 15% for LogReg
                    )
                    
                    # Format enhanced risk prediction for frontend
                    enhanced_risk_prediction_result = {
                        # Core prediction (enhanced)
                        'risk_level': enhanced_result['risk_level'],
                        'confidence': enhanced_result['confidence'],
                        'confidence_percentage': enhanced_result['confidence_percentage'],
                        'timeline_months': enhanced_result['timeline_months'],
                        'recommendations': enhanced_result['recommendations'],
                        
                        # ENHANCED: Detailed breakdown
                        'enhancement_details': enhanced_result['enhancement_details'],
                        'probability_breakdown': enhanced_result['probability_breakdown'],
                        'confidence_breakdown': enhanced_result['confidence_breakdown'],
                        
                        # Original data for comparison
                        'original_logreg_prediction': {
                            'risk_level': original_logreg_result['risk_level'],
                            'confidence': original_logreg_result['confidence'],
                            'confidence_percentage': round(original_logreg_result['confidence'] * 100, 1)
                        },
                        
                        # Context info
                        'used_realtime_data': enhanced_result['used_realtime_data'],
                        'air_quality_city': enhanced_result['air_quality_city'],
                        'air_quality_station': enhanced_result['air_quality_station'],
                        'enhancement_applied': True,
                        'aqi_influence_percentage': int(enhanced_result['enhancement_details']['aqi_weight_used'] * 100)
                    }
                    
                    logger.info(f"🎯 Enhanced prediction: {enhanced_result['risk_level']} (confidence: {enhanced_result['confidence']:.3f})")
                    logger.info(f"⚖️ AQI influence: {enhanced_risk_prediction_result['aqi_influence_percentage']}%")
                    
                except Exception as logreg_error:
                    logger.error(f"❌ Enhanced risk prediction error: {logreg_error}")
                    enhanced_risk_prediction_result = None
            
            # Clean up temporary file
            default_storage.delete(image_path)
            
            # Prepare ENHANCED response
            response_data = {
                'success': True,
                'classification': prediction_result['classification'],
                'confidence': prediction_result['confidence'],
                'confidence_percentage': round(prediction_result['confidence'] * 100, 1),
                'all_probabilities': prediction_result['all_probabilities'],
                'air_quality_data': air_quality_data,
                
                # ENHANCED: System enhancement info
                'data_enhancement': {
                    'total_cities_available': 14,  # Updated count
                    'data_source_type': data_source,
                    'real_time_enabled': data_source == 'aqicn_realtime',
                    'aqi_weighting_applied': enhanced_risk_prediction_result is not None,
                    'enhancement_version': '2.0_AQI_Weighted'
                }
            }
            
            if enhanced_risk_prediction_result:
                response_data['risk_prediction'] = enhanced_risk_prediction_result
                logger.info(f"📤 Sending enhanced response with AQI-weighted prediction")
            
            return JsonResponse(response_data)
            
        except Exception as e:
            # Clean up temporary file if error occurs
            if default_storage.exists(image_path):
                default_storage.delete(image_path)
            raise e
            
    except Exception as e:
        logger.error(f"❌ Enhanced prediction error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }, status=500)

# Keep all other existing functions unchanged
@csrf_exempt  
@require_http_methods(["GET"])
def get_cities_simple(request):
    """Get list of Indonesian cities dengan real-time preview option"""
    show_realtime_preview = request.GET.get('preview', '').lower() == 'true'
    
    # Get Indonesian cities
    indonesian_cities_info = get_available_indonesian_cities_info()
    
    # Add real-time preview jika diminta
    if show_realtime_preview:
        logger.info("🔄 Fetching real-time preview for Indonesian cities...")
        for city_info in indonesian_cities_info:
            try:
                from .aqicn_integration import get_real_time_air_quality
                realtime_data = get_real_time_air_quality(city_info['code'], fallback_to_static=True)
                if realtime_data:
                    city_info['aqi'] = realtime_data.get('aqi', city_info.get('aqi_estimate', 'N/A'))
                    city_info['pm25'] = realtime_data.get('pm25')
                    city_info['data_source'] = realtime_data.get('data_source', 'static')
                    city_info['last_updated'] = realtime_data.get('last_update', 'Unknown')
                    city_info['station_name'] = realtime_data.get('station_name', 'Unknown')
            except Exception as e:
                logger.warning(f"Could not get real-time data for {city_info['code']}: {e}")
                city_info['data_source'] = 'static_fallback'
    
    return JsonResponse({
        'success': True,
        'cities': indonesian_cities_info,
        'total_cities': len(indonesian_cities_info),
        'realtime_preview': show_realtime_preview,
        'country_focus': 'Indonesia',
        'data_provider': 'aqicn.org',
        'enhancement_version': '2.0_AQI_Weighted'
    })

@csrf_exempt
@require_http_methods(["GET"]) 
def get_air_quality_simple(request, city_code):
    """Get air quality data untuk Indonesian cities dengan real-time aqicn.org"""
    try:
        air_quality_data = get_country_air_quality_data(city_code)
        
        return JsonResponse({
            'success': True,
            'data': air_quality_data,
            'city_info': {
                'code': city_code,
                'available_cities': 14,
                'data_source': air_quality_data.get('data_source', 'unknown'),
                'enhancement_version': '2.0_AQI_Weighted'
            }
        })
    except Exception as e:
        logger.error(f"Error getting air quality for {city_code}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'city_code': city_code
        }, status=500)

def get_country_air_quality_data(city_code):
    """
    ENHANCED: Get air quality data dengan Indonesian cities real-time integration
    """
    try:
        from .aqicn_integration import get_real_time_air_quality
        
        logger.info(f"🌍 Attempting real-time data for: {city_code}")
        realtime_data = get_real_time_air_quality(city_code, fallback_to_static=True)
        
        if realtime_data:
            data_source = realtime_data.get('data_source', 'unknown')
            city_name = realtime_data.get('city_name', city_code)
            aqi = realtime_data.get('aqi', 'N/A')
            
            logger.info(f"✅ Air quality data for {city_code} → {city_name}: AQI={aqi}, Source={data_source}")
            return realtime_data
        else:
            logger.warning(f"⚠️ No real-time data available, falling back to static for {city_code}")
            return get_static_air_quality_data(city_code)
            
    except Exception as e:
        logger.error(f"❌ Error in get_country_air_quality_data for {city_code}: {e}")
        logger.info(f"🔄 Using static fallback for {city_code}")
        return get_static_air_quality_data(city_code)

def get_static_air_quality_data(city_code):
    """Static air quality data sebagai ultimate fallback"""
    # Original static data untuk backward compatibility
    static_country_data = {
        'indonesia': {
            'aqi': 154, 'pm25': 67.92, 'pm10': 75.52, 'pm1': 39.60,
            'o3': 45.0, 'no2': 31.0, 'so2': 15.0, 'co': 2.5,
            'humidity': 45.61, 'temperature': 31.16,
            'country_code': 'indonesia', 'data_source': 'static_original'
        }
    }
    
    # Enhanced: Add static fallback untuk Indonesian cities
    indonesian_static_fallback = {
        'jakarta': {'aqi': 154, 'pm25': 67.92, 'city_name': 'jakarta'},
        'medan': {'aqi': 162, 'pm25': 65.0, 'city_name': 'medan'},
        'semarang': {'aqi': 95, 'pm25': 35.0, 'city_name': 'semarang'},
        'palembang': {'aqi': 43, 'pm25': 15.0, 'city_name': 'palembang'},
        'malang': {'aqi': 78, 'pm25': 25.0, 'city_name': 'malang'},
        'jogjakarta': {'aqi': 123, 'pm25': 45.0, 'city_name': 'jogjakarta'},
        'pontianak': {'aqi': 62, 'pm25': 20.0, 'city_name': 'pontianak'},
        'bengkulu': {'aqi': 68, 'pm25': 22.0, 'city_name': 'bengkulu'},
        'pekanbaru': {'aqi': 163, 'pm25': 66.0, 'city_name': 'pekanbaru'},
        'bekasi': {'aqi': 151, 'pm25': 64.0, 'city_name': 'bekasi'},
        'tangerang': {'aqi': 151, 'pm25': 64.0, 'city_name': 'tangerang'},
        'depok': {'aqi': 123, 'pm25': 45.0, 'city_name': 'depok'},
        'batu': {'aqi': 78, 'pm25': 25.0, 'city_name': 'batu'}
    }
    
    # Try Indonesian city first, then country fallback
    if city_code.lower() in indonesian_static_fallback:
        base_data = indonesian_static_fallback[city_code.lower()]
        result = {
            'aqi': base_data['aqi'], 'pm25': base_data['pm25'],
            'pm10': base_data['pm25'] * 1.2, 'pm1': base_data['pm25'] * 0.6,
            'o3': 35.0, 'no2': 25.0, 'so2': 12.0, 'co': 2.0,
            'humidity': 60.0, 'temperature': 28.0,
            'country_code': 'indonesia', 'city_name': base_data['city_name'],
            'data_source': 'static_indonesian_fallback'
        }
    else:
        result = static_country_data.get(city_code.lower(), static_country_data['indonesia'])
        result['data_source'] = 'static_original_fallback'
    
    return result

def get_available_indonesian_cities_info():
    """Get informasi lengkap tentang Indonesian cities yang tersedia"""
    cities_info = [
        {'code': 'indonesia', 'name': 'Indonesia (Default to Jakarta)', 'region': 'Nasional', 'aqi_estimate': 151},
        {'code': 'jakarta', 'name': 'Jakarta', 'region': 'DKI Jakarta', 'aqi_estimate': 151},
        {'code': 'medan', 'name': 'Medan', 'region': 'Sumatera Utara', 'aqi_estimate': 162},
        {'code': 'semarang', 'name': 'Semarang', 'region': 'Jawa Tengah', 'aqi_estimate': 95},
        {'code': 'palembang', 'name': 'Palembang', 'region': 'Sumatera Selatan', 'aqi_estimate': 43},
        {'code': 'malang', 'name': 'Malang', 'region': 'Jawa Timur', 'aqi_estimate': 78},
        {'code': 'jogjakarta', 'name': 'Yogyakarta', 'region': 'DI Yogyakarta', 'aqi_estimate': 123},
        {'code': 'pontianak', 'name': 'Pontianak', 'region': 'Kalimantan Barat', 'aqi_estimate': 62},
        {'code': 'bengkulu', 'name': 'Bengkulu', 'region': 'Bengkulu', 'aqi_estimate': 68},
        {'code': 'pekanbaru', 'name': 'Pekanbaru', 'region': 'Riau', 'aqi_estimate': 163},
        {'code': 'bekasi', 'name': 'Bekasi', 'region': 'Jawa Barat', 'aqi_estimate': 151},
        {'code': 'tangerang', 'name': 'Tangerang', 'region': 'Banten', 'aqi_estimate': 151},
        {'code': 'depok', 'name': 'Depok', 'region': 'Jawa Barat', 'aqi_estimate': 123},
        {'code': 'batu', 'name': 'Batu', 'region': 'Jawa Timur', 'aqi_estimate': 78}
    ]
    
    # Add AQI categories
    for city in cities_info:
        aqi = city['aqi_estimate']
        if aqi <= 50:
            city['category'] = 'Good'
            city['description'] = 'Baik'
        elif aqi <= 100:
            city['category'] = 'Moderate'
            city['description'] = 'Sedang'
        elif aqi <= 150:
            city['category'] = 'Unhealthy for Sensitive Groups'
            city['description'] = 'Tidak Sehat untuk Kelompok Sensitif'
        else:
            city['category'] = 'Unhealthy'
            city['description'] = 'Tidak Sehat'
    
    return cities_info