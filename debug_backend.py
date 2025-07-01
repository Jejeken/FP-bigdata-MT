# debug_backend.py - Place this in lung_prediction_system root
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

print("🔍 DEBUGGING BACKEND ISSUES")
print("="*50)

# Test 1: Check cities function
print("\n1️⃣ Testing get_available_indonesian_cities_info():")
try:
    from prediction.views import get_available_indonesian_cities_info
    cities = get_available_indonesian_cities_info()
    print(f"✅ Cities function returned: {len(cities)} cities")
    for i, city in enumerate(cities[:10]):
        print(f"   {i+1:2d}. {city['name']} ({city['code']}) - AQI: {city['aqi_estimate']}")
    if len(cities) > 10:
        print(f"   ... and {len(cities) - 10} more cities")
except Exception as e:
    print(f"❌ Cities function error: {e}")

# Test 2: Check cities API endpoint
print("\n2️⃣ Testing cities API endpoint:")
try:
    from django.test import Client
    client = Client()
    
    # Test both URL patterns
    endpoints = ['/prediction/cities/', '/prediction/cities/?preview=true']
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        print(f"   {endpoint}: Status {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            print(f"   ✅ Success: {data.get('success')}")
            print(f"   📊 Cities count: {len(data.get('cities', []))}")
            print(f"   🔄 Realtime preview: {data.get('realtime_preview')}")
        else:
            print(f"   ❌ Error: {response.content[:200]}")
        print()
        
except Exception as e:
    print(f"❌ Cities API error: {e}")

# Test 3: Check aqicn integration
print("\n3️⃣ Testing aqicn integration:")
try:
    from prediction.aqicn_integration import get_real_time_air_quality, INDONESIAN_CITIES
    
    print(f"   📊 INDONESIAN_CITIES available: {len(INDONESIAN_CITIES)}")
    
    # Test real-time function
    test_city = 'jakarta'
    print(f"   🧪 Testing {test_city}...")
    
    data = get_real_time_air_quality(test_city, fallback_to_static=True)
    if data:
        print(f"   ✅ {test_city}: AQI={data.get('aqi')}, Source={data.get('data_source')}")
        print(f"   📍 Station: {data.get('station_name', 'N/A')}")
        print(f"   🕐 Update: {data.get('last_update', 'N/A')}")
    else:
        print(f"   ❌ {test_city}: No data returned")
        
except Exception as e:
    print(f"❌ aqicn integration error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check air quality API endpoint
print("\n4️⃣ Testing air quality API endpoint:")
try:
    from django.test import Client
    client = Client()
    
    test_cities = ['indonesia', 'jakarta', 'medan']
    
    for city in test_cities:
        endpoint = f'/prediction/air-quality/{city}/'
        response = client.get(endpoint)
        print(f"   {endpoint}: Status {response.status_code}")
        
        if response.status_code == 200:
            import json
            data = json.loads(response.content)
            if data.get('success'):
                air_data = data.get('data', {})
                print(f"   ✅ {city}: AQI={air_data.get('aqi')}, Source={air_data.get('data_source')}")
            else:
                print(f"   ⚠️ {city}: API success=False, error={data.get('error')}")
        else:
            print(f"   ❌ {city}: HTTP Error {response.status_code}")
            
except Exception as e:
    print(f"❌ Air quality API error: {e}")

# Test 5: Direct aqicn API test
print("\n5️⃣ Testing direct aqicn API:")
try:
    import requests
    api_key = '452d02260843c9375aa32ee052ea2abc527a2a87'
    
    test_url = f'https://api.waqi.info/feed/jakarta/?token={api_key}'
    response = requests.get(test_url, timeout=10)
    
    print(f"   Direct aqicn test: Status {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'ok':
            aqi = data.get('data', {}).get('aqi')
            print(f"   ✅ Direct aqicn working: AQI={aqi}")
        else:
            print(f"   ⚠️ aqicn API status: {data.get('status')}")
    else:
        print(f"   ❌ Direct aqicn failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Direct aqicn error: {e}")

print("\n" + "="*50)
print("🎯 DEBUGGING COMPLETED")