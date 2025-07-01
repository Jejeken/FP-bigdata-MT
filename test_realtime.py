# test_realtime_data.py - FIXED VERSION

import os
import sys
import django
import time
from datetime import datetime
import requests # <-- DIPINDAHKAN KE ATAS

# --- Pastikan semua import modul aplikasi Anda juga di atas ---
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

# --- Import dari modul Anda dipindahkan ke sini ---
from prediction.aqicn_integration import get_real_time_air_quality
from prediction.views import get_country_air_quality_data


print("🔍 TESTING REAL-TIME DATA VERIFICATION")
print("="*60)

def test_data_freshness():
    """Test if data actually changes over time"""
    
    # Import sudah dipindahkan ke atas, tidak perlu lagi di sini
    
    test_cities = ['jakarta', 'medan', 'semarang']
    
    print("\n📊 CURRENT DATA SNAPSHOT:")
    print("-" * 40)
    
    for city in test_cities:
        try:
            # Test direct aqicn integration
            direct_data = get_real_time_air_quality(city, fallback_to_static=True)
            
            # Test through views (what frontend gets)
            view_data = get_country_air_quality_data(city)
            
            print(f"\n🏙️ {city.upper()}:")
            print(f"    Direct AQI: {direct_data.get('aqi', 'N/A')}")
            print(f"    View AQI: {view_data.get('aqi', 'N/A')}")
            print(f"    Source: {direct_data.get('data_source', 'unknown')}")
            print(f"    Station: {direct_data.get('station_name', 'N/A')}")
            print(f"    Last Update: {direct_data.get('last_update', 'N/A')}")
            print(f"    Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"    ❌ Error for {city}: {e}")

def test_api_freshness():
    """Test aqicn.org API directly for freshness"""
    
    # Import sudah dipindahkan ke atas, tidak perlu lagi di sini
    
    api_key = '452d02260843c9375aa32ee052ea2abc527a2a87'
    test_cities = ['jakarta', 'medan', 'semarang']
    
    print(f"\n🌐 DIRECT AQICN.ORG API TEST:")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") # <--- SEKARANG TIDAK AKAN ERROR
    print("-" * 40)
    
    for city in test_cities:
        try:
            url = f'https://api.waqi.info/feed/{city}/?token={api_key}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    main_data = data.get('data', {})
                    aqi = main_data.get('aqi')
                    station = main_data.get('city', {}).get('name', 'Unknown')
                    update_time = main_data.get('time', {}).get('s', 'Unknown')
                    
                    print(f"\n🏙️ {city.upper()} (Direct API):")
                    print(f"    AQI: {aqi}")
                    print(f"    Station: {station}")
                    print(f"    Data Time: {update_time}")
                    print(f"    API Status: {data.get('status')}")
                    
                    # Check if data is recent
                    try:
                        current_time = datetime.now()
                        print(f"    Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        # Parse update time and compare
                        if update_time != 'Unknown':
                            # Penyesuaian: beberapa API mungkin menyertakan info timezone
                            data_time_str = update_time.split(' ')[0] + ' ' + update_time.split(' ')[1]
                            data_time = datetime.strptime(data_time_str, '%Y-%m-%d %H:%M:%S')
                            time_diff = current_time - data_time
                            hours_old = time_diff.total_seconds() / 3600
                            print(f"    Data Age: {hours_old:.1f} hours ago")
                            
                            if hours_old < 2:
                                print(f"    ✅ Data is FRESH (< 2 hours old)")
                            elif hours_old < 24:
                                print(f"    ⚠️ Data is moderate (< 24 hours old)")
                            else:
                                print(f"    ❌ Data is OLD (> 24 hours old)")
                    except Exception as e:
                        print(f"    ⚠️ Could not parse time: {e}")
                        
                else:
                    print(f"    ❌ {city}: API status = {data.get('status')}")
            else:
                print(f"    ❌ {city}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ {city}: Error - {e}")

def test_multiple_requests():
    """Test if data changes between requests"""
    
    # Import sudah dipindahkan ke atas
    
    city = 'jakarta'
    print(f"\n🔄 MULTIPLE REQUESTS TEST ({city}):")
    print("-" * 40)
    
    results = []
    
    for i in range(3):
        try:
            data = get_real_time_air_quality(city, fallback_to_static=False)  # Force real-time
            
            if data and data.get('data_source') == 'aqicn_realtime':
                result = {
                    'attempt': i + 1,
                    'aqi': data.get('aqi'),
                    'pm25': data.get('pm25'),
                    'station': data.get('station_name'),
                    'update': data.get('last_update'),
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
                results.append(result)
                
                print(f"    Request {i+1} ({result['timestamp']}): AQI={result['aqi']}, PM2.5={result['pm25']}")
            else:
                print(f"    Request {i+1}: Fallback data or error")
                
        except Exception as e:
            print(f"    Request {i+1}: Error - {e}")
            
        if i < 2:  # Small delay between requests
            time.sleep(2)
    
    # Analysis
    if len(results) >= 2:
        first = results[0]
        last = results[-1]
        
        print(f"\n📈 ANALYSIS:")
        print(f"    First AQI: {first['aqi']} at {first['timestamp']}")
        print(f"    Last AQI: {last['aqi']} at {last['timestamp']}")
        
        if first['aqi'] == last['aqi'] and first['update'] == last['update']:
            print(f"    📊 Data CONSISTENT (same values, same update time)")
            print(f"    ⚡ This indicates data is from same API snapshot")
        else:
            print(f"    🔄 Data CHANGED between requests")
            print(f"    ⚡ This indicates truly dynamic data")

if __name__ == "__main__":
    print("Starting real-time data verification...")
    
    # Test 1: Current data snapshot
    test_data_freshness()
    
    # Test 2: Direct API freshness
    test_api_freshness()
    
    # Test 3: Multiple requests
    test_multiple_requests()
    
    print("\n" + "="*60)
    print("🎯 VERIFICATION COMPLETED")
    print("\n💡 INTERPRETATION:")
    print("✅ If 'Data Age' < 2 hours → Truly real-time")
    print("⚠️ If 'Data Age' > 24 hours → Data might be cached/old")
    print("📊 If multiple requests show same values → Normal (data updated hourly)")
    print("🔄 If data changes between requests → Highly dynamic")