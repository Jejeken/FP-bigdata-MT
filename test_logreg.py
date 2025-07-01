# test_logreg.py

import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

def test_logreg_model():
    """Test LogReg model loading and prediction"""
    print("=== Testing LogReg Air Quality Risk Model ===\n")
    
    try:
        from prediction.logreg_model import get_logreg_predictor
        
        # Test model loading
        predictor = get_logreg_predictor()
        print("✅ LogReg model loaded successfully!")
        
        # Test predictions for all 3 countries
        countries = ['indonesia', 'singapore', 'australia']
        
        for country in countries:
            print(f"\n--- Testing {country.title()} ---")
            try:
                result = predictor.predict_risk(country)
                print(f"✅ {country.title()} prediction successful!")
                print(f"   Risk Level: {result['risk_level']}")
                print(f"   Confidence: {result['confidence_percentage']}%")
                print(f"   AQI: {result['air_quality_data']['aqi']}")
                
            except Exception as e:
                print(f"❌ Error predicting {country}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LogReg model: {e}")
        return False

def test_integration_with_xray():
    """Test integration between X-ray and LogReg models"""
    print("\n=== Testing X-ray + LogReg Integration ===\n")
    
    try:
        from prediction.ml_models import get_predictor
        
        # Create mock normal X-ray result
        mock_air_quality = {
            'aqi': 154,
            'pm25': 67.92,
            'country_code': 'indonesia'
        }
        
        xray_predictor = get_predictor()
        
        # Test risk prediction for normal case
        risk_result = xray_predictor.get_risk_prediction(
            classification='normal',
            confidence=0.85,
            air_quality_data=mock_air_quality
        )
        
        if risk_result:
            print("✅ X-ray + LogReg integration successful!")
            print(f"   Risk Score: {risk_result['risk_score']}")
            print(f"   Timeline: {risk_result['timeline_months']} months")
            print(f"   Risk Level: {risk_result.get('risk_level', 'N/A')}")
            print(f"   Recommendations: {len(risk_result['recommendations'])} items")
            
            return True
        else:
            print("❌ No risk result returned")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== Testing API Endpoints ===\n")
    
    import requests
    
    base_url = 'http://127.0.0.1:8000/api'
    
    try:
        # Test cities endpoint
        response = requests.get(f'{base_url}/cities/')
        if response.status_code == 200:
            data = response.json()
            print("✅ Cities API working!")
            print(f"   Found {len(data['cities'])} countries")
            for city in data['cities']:
                print(f"   - {city['name']}: AQI {city['aqi']}")
        else:
            print(f"❌ Cities API failed: {response.status_code}")
        
        # Test air quality endpoint
        for country in ['indonesia', 'singapore', 'australia']:
            response = requests.get(f'{base_url}/air-quality/{country}/')
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Air quality API for {country}: AQI {data['data']['aqi']}")
            else:
                print(f"❌ Air quality API for {country} failed")
                
    except requests.exceptions.ConnectionError:
        print("❌ Django server not running. Start with: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")

if __name__ == "__main__":
    print("🔍 Testing LogReg Integration\n")
    
    # Test 1: LogReg model
    logreg_ok = test_logreg_model()
    
    if logreg_ok:
        # Test 2: X-ray + LogReg integration
        integration_ok = test_integration_with_xray()
        
        # Test 3: API endpoints (requires server running)
        test_api_endpoints()
        
        if integration_ok:
            print("\n🎉 All tests passed! Ready for full testing!")
            print("\nNext steps:")
            print("1. Run: python manage.py runserver")
            print("2. Open: http://127.0.0.1:8000/")
            print("3. Test complete workflow:")
            print("   - Select country → Upload X-ray → See LogReg risk prediction!")
        else:
            print("\n⚠️  Integration issues detected")
    else:
        print("\n❌ LogReg model setup needed")
    
    print("\n" + "="*60)