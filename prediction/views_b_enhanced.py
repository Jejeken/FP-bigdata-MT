# prediction/views.py - COMPLETE VERSION WITH INDONESIAN CITIES INTEGRATION
# Enhanced version dengan real-time aqicn.org data untuk 13 kota Indonesia
# Replace existing views.py dengan file ini setelah backup

import os
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import render
import logging

# ENHANCED: Import aqicn integration untuk real-time Indonesian air quality data
from .aqicn_integration import get_real_time_air_quality, INDONESIAN_CITIES

logger = logging.getLogger(__name__)

def index(request):
    """Serve the main frontend page"""
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def predict_xray_simple(request):
    """
    Main prediction endpoint dengan ENHANCED real-time Indonesian air quality
    UPGRADED: Sekarang menggunakan real-time data dari 13 kota Indonesia
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
        city_code = request.POST.get('city', 'indonesia')  # Default ke 'indonesia' = Jakarta
        
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
            
            # ===== ENHANCED: Get REAL-TIME Indonesian air quality data =====
            logger.info(f"🌍 Fetching real-time air quality for: {city_code}")
            air_quality_data = get_country_air_quality_data(city_code)  # Now uses REAL-TIME data!
            
            data_source = air_quality_data.get('data_source', 'unknown')
            aqi = air_quality_data.get('aqi', 'N/A')
            city_name = air_quality_data.get('city_name', city_code)
            
            logger.info(f"📊 Air Quality - {city_name}: AQI={aqi}, Source={data_source}")
            
            # Get risk prediction for NORMAL cases
            risk_prediction = None
            if prediction_result['classification'].lower().strip() == 'normal':
                logger.info(f"✅ Running LogReg for NORMAL case with {data_source} data...")
                try:
                    logreg_predictor = get_logreg_predictor()
                    logreg_result = logreg_predictor.predict_risk(city_code)
                    
                    # Format risk prediction dengan enhanced info
                    risk_prediction = {
                        'risk_level': logreg_result['risk_level'],
                        'confidence': logreg_result['confidence'],
                        'confidence_percentage': round(logreg_result['confidence'] * 100, 1),
                        'timeline_months': logreg_result['timeline_months'],
                        'recommendations': (
                            logreg_result['recommendations']['general'] + 
                            logreg_result['recommendations']['specific']
                        )[:7],
                        'logreg_details': logreg_result,
                        'used_realtime_data': data_source == 'aqicn_realtime',
                        'air_quality_city': city_name,
                        'air_quality_station': air_quality_data.get('station_name', 'Unknown')
                    }
                    
                    realtime_status = "real-time" if data_source == 'aqicn_realtime' else "fallback"
                    logger.info(f"🎯 LogReg result: {logreg_result['risk_level']} (using {realtime_status} data from {city_name})")
                    
                except Exception as logreg_error:
                    logger.error(f"❌ LogReg error: {logreg_error}")
                    risk_prediction = None
            
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
                # ENHANCED: Add Indonesian cities info
                'available_cities': get_available_indonesian_cities_info(),
                'selected_city': city_code,
                'data_enhancement': {
                    'total_cities_available': len(INDONESIAN_CITIES),
                    'data_source_type': data_source,
                    'real_time_enabled': data_source == 'aqicn_realtime'
                }
            }
            
            if risk_prediction:
                response_data['risk_prediction'] = risk_prediction
                realtime_flag = risk_prediction.get('used_realtime_data', False)
                logger.info(f"📤 Sending response with risk prediction (realtime: {realtime_flag})")
            
            return JsonResponse(response_data)
            
        except Exception as e:
            # Clean up temporary file if error occurs
            if default_storage.exists(image_path):
                default_storage.delete(image_path)
            raise e
            
    except Exception as e:
        logger.error(f"❌ Prediction error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }, status=500)

@csrf_exempt  
@require_http_methods(["GET"])
def get_cities_simple(request):
    """
    ENHANCED: Get list of Indonesian cities dengan real-time preview option
    """
    # Check if real-time preview requested
    show_realtime_preview = request.GET.get('preview', '').lower() == 'true'
    
    # ENHANCED: Indonesian cities dengan AQI info
    indonesian_cities_info = get_available_indonesian_cities_info()
    
    # Add real-time preview jika diminta
    if show_realtime_preview:
        logger.info("🔄 Fetching real-time preview for Indonesian cities...")
        for city_info in indonesian_cities_info:
            try:
                realtime_data = get_real_time_air_quality(city_info['code'], fallback_to_static=True)
                if realtime_data:
                    city_info['aqi'] = realtime_data.get('aqi', city_info.get('aqi', 'N/A'))
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
        'data_provider': 'aqicn.org'
    })

@csrf_exempt
@require_http_methods(["GET"]) 
def get_air_quality_simple(request, city_code):
    """
    ENHANCED: Get air quality data untuk Indonesian cities dengan real-time aqicn.org
    """
    try:
        air_quality_data = get_country_air_quality_data(city_code)
        
        return JsonResponse({
            'success': True,
            'data': air_quality_data,
            'city_info': {
                'code': city_code,
                'available_cities': len(INDONESIAN_CITIES),
                'data_source': air_quality_data.get('data_source', 'unknown')
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
    ENHANCED MAIN FUNCTION: Get air quality data dengan Indonesian cities real-time integration
    
    Ini adalah CORE UPGRADE yang mengganti static data dengan real-time Indonesian data
    sambil maintain perfect backward compatibility.
    """
    try:
        # ENHANCED: Try real-time Indonesian data first
        logger.info(f"🌍 Attempting real-time data for: {city_code}")
        realtime_data = get_real_time_air_quality(city_code, fallback_to_static=True)
        
        if realtime_data:
            data_source = realtime_data.get('data_source', 'unknown')
            city_name = realtime_data.get('city_name', city_code)
            aqi = realtime_data.get('aqi', 'N/A')
            
            logger.info(f"✅ Air quality data for {city_code} → {city_name}: AQI={aqi}, Source={data_source}")
            return realtime_data
        else:
            # Fallback ke original static data
            logger.warning(f"⚠️ No real-time data available, falling back to static for {city_code}")
            return get_static_air_quality_data(city_code)
            
    except Exception as e:
        logger.error(f"❌ Error in get_country_air_quality_data for {city_code}: {e}")
        # Ultimate fallback: static data
        logger.info(f"🔄 Using static fallback for {city_code}")
        return get_static_air_quality_data(city_code)

def get_static_air_quality_data(city_code):
    """
    ORIGINAL static air quality data sebagai ultimate fallback
    Maintained untuk compatibility dan emergency fallback
    """
    # Original static data untuk backward compatibility
    static_country_data = {
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
            'country_code': 'indonesia',
            'data_source': 'static_original'
        }
    }
    
    # ENHANCED: Add static fallback untuk Indonesian cities
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
            'aqi': base_data['aqi'],
            'pm25': base_data['pm25'],
            'pm10': base_data['pm25'] * 1.2,  # Estimate
            'pm1': base_data['pm25'] * 0.6,   # Estimate
            'o3': 35.0, 'no2': 25.0, 'so2': 12.0, 'co': 2.0,
            'humidity': 60.0, 'temperature': 28.0,
            'country_code': 'indonesia',
            'city_name': base_data['city_name'],
            'data_source': 'static_indonesian_fallback'
        }
    else:
        # Original country fallback
        result = static_country_data.get(city_code.lower(), static_country_data['indonesia'])
        result['data_source'] = 'static_original_fallback'
    
    return result

def get_available_indonesian_cities_info():
    """
    ENHANCED: Get informasi lengkap tentang Indonesian cities yang tersedia
    """
    # Base info untuk Indonesian cities
    cities_info = [
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
    
    # Add backward compatibility untuk 'indonesia'
    cities_info.insert(0, {
        'code': 'indonesia',
        'name': 'Indonesia (Default to Jakarta)',
        'region': 'Nasional',
        'aqi_estimate': 151,
        'category': 'Unhealthy for Sensitive Groups',
        'description': 'Tidak Sehat untuk Kelompok Sensitif (Default Jakarta)'
    })
    
    return cities_info

# ===== NEW ENHANCED ENDPOINTS untuk Indonesian Cities =====

@csrf_exempt
@require_http_methods(["GET"])
def get_indonesian_cities_list(request):
    """
    NEW: Dedicated endpoint untuk list Indonesian cities
    """
    try:
        cities_info = get_available_indonesian_cities_info()
        
        return JsonResponse({
            'success': True,
            'indonesian_cities': cities_info,
            'total_cities': len(cities_info),
            'data_provider': 'aqicn.org',
            'last_updated': 'real-time'
        })
        
    except Exception as e:
        logger.error(f"Error getting Indonesian cities list: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_realtime_indonesian_data(request, city_code):
    """
    NEW: Dedicated endpoint untuk real-time Indonesian city data
    """
    try:
        force_realtime = request.GET.get('force_realtime', '').lower() == 'true'
        fallback = not force_realtime
        
        data = get_real_time_air_quality(city_code, fallback_to_static=fallback)
        
        if data:
            return JsonResponse({
                'success': True,
                'data': data,
                'is_realtime': data.get('data_source') == 'aqicn_realtime',
                'city_code': city_code,
                'provider': 'aqicn.org'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No data available for this city',
                'city_code': city_code,
                'available_cities': list(INDONESIAN_CITIES.keys())
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error in realtime Indonesian data endpoint for {city_code}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'city_code': city_code
        }, status=500)

# ===== TESTING & MONITORING ENDPOINTS =====

@csrf_exempt
@require_http_methods(["GET"])
def test_indonesian_integration(request):
    """
    NEW: Testing endpoint untuk verify Indonesian cities integration
    """
    if not request.user.is_staff and not request.GET.get('allow_test'):
        return JsonResponse({
            'success': False,
            'error': 'Access denied. Add ?allow_test=true for testing.'
        }, status=403)
    
    results = {}
    sample_cities = ['indonesia', 'jakarta', 'medan', 'semarang', 'palembang']
    
    for city in sample_cities:
        try:
            data = get_real_time_air_quality(city, fallback_to_static=True)
            results[city] = {
                'success': True,
                'aqi': data.get('aqi'),
                'pm25': data.get('pm25'),
                'data_source': data.get('data_source'),
                'city_name': data.get('city_name'),
                'station_name': data.get('station_name')
            }
        except Exception as e:
            results[city] = {
                'success': False,
                'error': str(e)
            }
    
    # Overall status
    realtime_count = sum(1 for result in results.values() 
                        if result.get('data_source') == 'aqicn_realtime')
    
    return JsonResponse({
        'success': True,
        'test_results': results,
        'summary': {
            'total_cities_tested': len(results),
            'realtime_sources': realtime_count,
            'fallback_sources': len(results) - realtime_count,
            'integration_health': 'excellent' if realtime_count >= 4 
                                 else 'good' if realtime_count >= 2 
                                 else 'needs_attention',
            'total_available_cities': len(INDONESIAN_CITIES),
            'data_provider': 'aqicn.org'
        }
    })