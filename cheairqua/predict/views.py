from django.shortcuts import render
from django.http import JsonResponse
from .models import air_quality, extract_pm25_value, calculate_aqi_pm25
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Renders the main React application page."""
    return render(request, 'index.html')

def air_quality_api(request, location_id):
    """
    API endpoint to get air quality data for a given location_id.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    try:
        # 1. Fetch raw data from OpenAQ
        sensor_data_object = air_quality(location_id)

        # 2. Extract all sensor values into a dictionary
        all_values = extract_pm25_value(sensor_data_object)

        # 3. Get PM2.5 value for AQI calculation
        pm25_value = all_values

        # 4. Calculate AQI based on PM2.5
        aqi_data = calculate_aqi_pm25(pm25_value)

        # 5. Prepare the final JSON response
        response_data = {
            'location_id': location_id,
            'pm25_value': all_values,
            'aqi_data': aqi_data
        }

        return JsonResponse(response_data)

    except ValueError as e:
        logger.warning(f"Value error for location {location_id}: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error fetching air quality for location {location_id}: {e}", exc_info=True)
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)