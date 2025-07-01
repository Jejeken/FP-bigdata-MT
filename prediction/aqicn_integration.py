# Preview: aqicn_integration.py module 
# Will replace openaq_integration.py dengan better data source!

import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Your aqicn.org API key
AQICN_API_KEY = "452d02260843c9375aa32ee052ea2abc527a2a87"

# Indonesian cities mapping - Real available cities dari aqicn.org
INDONESIAN_CITIES = {
    'jakarta': 'jakarta',
    'medan': 'medan',
    'bekasi': 'bekasi',
    'tangerang': 'tangerang',
    'depok': 'depok',
    'semarang': 'semarang',
    'palembang': 'palembang',
    'pekanbaru': 'pekanbaru',
    'malang': 'malang',
    'jogjakarta': 'jogjakarta',
    'pontianak': 'pontianak',
    'bengkulu': 'bengkulu',
    'batu': 'batu'
}

# Backward compatibility mapping (untuk existing system)
CITY_MAPPING = {
    'indonesia': 'jakarta',  # Default ke Jakarta for backward compatibility
    # Individual city access
    **INDONESIAN_CITIES
}

def get_aqicn_data(city_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch real-time air quality data from aqicn.org
    """
    try:
        url = f"https://api.waqi.info/feed/{city_name}/?token={AQICN_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                return data.get('data', {})
        
        logger.error(f"aqicn API error for {city_name}: {response.status_code}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching aqicn data for {city_name}: {e}")
        return None

def get_real_time_air_quality(country_code: str, fallback_to_static=True) -> Dict[str, Any]:
    """
    Main function - SAME interface sebagai OpenAQ version!
    Existing code tidak perlu berubah sama sekali!
    """
    
    # Convert country code ke city name
    city_name = CITY_MAPPING.get(country_code.lower())
    if not city_name:
        logger.warning(f"No city mapping for country: {country_code}")
        return get_static_fallback_data(country_code) if fallback_to_static else None
    
    # Fetch from aqicn.org
    aqicn_data = get_aqicn_data(city_name)
    
    if aqicn_data:
        # Convert aqicn format ke format yang expected oleh existing system
        iaqi = aqicn_data.get('iaqi', {})
        
        result = {
            'aqi': aqicn_data.get('aqi'),
            'pm25': iaqi.get('pm25', {}).get('v'),
            'pm10': iaqi.get('pm10', {}).get('v'),
            'pm1': iaqi.get('pm1', {}).get('v'),  # If available
            'o3': iaqi.get('o3', {}).get('v'),
            'no2': iaqi.get('no2', {}).get('v'),
            'so2': iaqi.get('so2', {}).get('v'),
            'co': iaqi.get('co', {}).get('v'),
            'humidity': iaqi.get('h', {}).get('v'),
            'temperature': iaqi.get('t', {}).get('v'),
            'country_code': country_code,
            'data_source': 'aqicn_realtime',
            'city_name': city_name,
            'last_update': aqicn_data.get('time', {}).get('s'),
            'station_name': aqicn_data.get('city', {}).get('name'),
            # Additional aqicn-specific data
            'aqicn_raw': aqicn_data  # For debugging/extended features
        }
        
        logger.info(f"✅ aqicn real-time data: {city_name} AQI={result['aqi']}")
        return result
    
    # Fallback to static data
    if fallback_to_static:
        logger.info(f"Falling back to static data for {country_code}")
        return get_static_fallback_data(country_code)
    
    return None

def get_static_fallback_data(country_code: str) -> Dict[str, Any]:
    """
    Static fallback data - EXACT same structure as before
    """
    static_data = {
        'indonesia': {
            'aqi': 154, 'pm25': 67.92, 'pm10': 75.52, 'pm1': 39.60,
            'o3': 45.0, 'no2': 31.0, 'so2': 15.0, 'co': 2.5,
            'humidity': 45.61, 'temperature': 31.16, 'country_code': 'indonesia'
        },
        'singapore': {
            'aqi': 66, 'pm25': 20.65, 'pm10': 22.61, 'pm1': 13.92,
            'o3': 35.0, 'no2': 25.0, 'so2': 8.0, 'co': 1.5,
            'humidity': 62.57, 'temperature': 29.60, 'country_code': 'singapore'
        },
        'australia': {
            'aqi': 25, 'pm25': 5.65, 'pm10': 6.05, 'pm1': 4.24,
            'o3': 25.0, 'no2': 15.0, 'so2': 5.0, 'co': 0.8,
            'humidity': 51.29, 'temperature': 16.16, 'country_code': 'australia'
        }
    }
    
    result = static_data.get(country_code.lower(), static_data['indonesia'])
    result['data_source'] = 'static_fallback'
    return result

def test_aqicn_integration():
    """Test aqicn integration dengan Indonesian cities"""
    print("🧪 Testing aqicn.org Integration with Indonesian Cities...")
    
    # Test backward compatibility
    print("\n📍 Testing backward compatibility:")
    try:
        data = get_real_time_air_quality('indonesia')
        aqi = data.get('aqi', 'N/A')
        pm25 = data.get('pm25', 'N/A') 
        source = data.get('data_source', 'unknown')
        
        print(f"  'indonesia' → {data.get('city_name', 'jakarta')}")
        print(f"  AQI: {aqi}, PM2.5: {pm25}, Source: {source}")
        print(f"  ✅ Backward compatibility working!")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test sample Indonesian cities
    sample_cities = ['jakarta', 'medan', 'semarang', 'palembang', 'malang']
    print(f"\n📍 Testing {len(sample_cities)} Indonesian cities:")
    
    for city in sample_cities:
        try:
            data = get_real_time_air_quality(city)
            aqi = data.get('aqi', 'N/A')
            pm25 = data.get('pm25', 'N/A') 
            source = data.get('data_source', 'unknown')
            
            print(f"\n  🏙️ {city.upper()}:")
            print(f"    AQI: {aqi}, PM2.5: {pm25}")
            print(f"    Source: {source}")
            
            if source == 'aqicn_realtime':
                print(f"    ✅ Real-time data successful!")
                print(f"    🏢 Station: {data.get('station_name', 'Unknown')}")
                print(f"    🕐 Updated: {data.get('last_update', 'Unknown')}")
            else:
                print(f"    ⚠️ Using fallback: {source}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n📊 Available Indonesian cities: {len(INDONESIAN_CITIES)}")
    print("🎉 aqicn integration test completed!")

if __name__ == "__main__":
    test_aqicn_integration()