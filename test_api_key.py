import requests
api_key = '452d02260843c9375aa32ee052ea2abc527a2a87'

test_cities = [
    'jakarta', 'surabaya', 'bandung', 'medan', 'bekasi', 
    'tangerang', 'depok', 'semarang', 'palembang', 'makassar',
    'batam', 'bogor', 'pekanbaru', 'bandar-lampung', 'malang', 'jogjakarta', 'denpasar',
    'balikpapan', 'padang', 'manado', 'pontianak', 'ambon', 'banda-aceh','bengkulu','batu'
]

available_cities = []
print('🔍 Checking available Indonesian cities in aqicn.org...\n')

for city in test_cities:
    try:
        url = f'https://api.waqi.info/feed/{city}/?token={api_key}'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                city_info = data.get('data', {}).get('city', {})
                aqi = data.get('data', {}).get('aqi', 'N/A')
                
                available_cities.append({
                    'code': city,
                    'name': city_info.get('name', city),
                    'aqi': aqi
                })
                
                print(f'✅ {city.upper()}: {city_info.get("name", city)} (AQI: {aqi})')
            else:
                print(f'❌ {city.upper()}: Not available')
        else:
            print(f'❌ {city.upper()}: HTTP {response.status_code}')
            
    except Exception as e:
        print(f'❌ {city.upper()}: Error - {e}')

print(f'\n📊 Found {len(available_cities)} available Indonesian cities')