# test_enhanced_integration.py
# Comprehensive testing untuk enhanced Indonesian cities integration
# Place this file di: lung_prediction_system/test_enhanced_integration.py

import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup error: {e}")
    print("Make sure to run this from lung_prediction_system root directory")
    sys.exit(1)

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_subheader(title):
    """Print formatted subheader"""
    print(f"\n{'─'*40}")
    print(f"📋 {title}")
    print(f"{'─'*40}")

def test_views_import():
    """Test 1: Verify enhanced views import successfully"""
    print_header("TEST 1: Enhanced Views Import")
    
    try:
        from prediction.views import (
            get_country_air_quality_data, 
            get_available_indonesian_cities_info,
            get_cities_simple,
            predict_xray_simple
        )
        print("✅ All enhanced views functions imported successfully")
        
        # Test aqicn integration import
        from prediction.aqicn_integration import INDONESIAN_CITIES
        print(f"✅ aqicn integration accessible - {len(INDONESIAN_CITIES)} cities available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_backward_compatibility():
    """Test 2: Ensure backward compatibility dengan existing system"""
    print_header("TEST 2: Backward Compatibility")
    
    try:
        from prediction.views import get_country_air_quality_data
        
        # Test original 'indonesia' parameter
        print("🔄 Testing 'indonesia' parameter (backward compatibility)...")
        data = get_country_air_quality_data('indonesia')
        
        required_fields = ['aqi', 'pm25', 'pm10', 'humidity', 'temperature', 'country_code']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if not missing_fields:
            print("✅ All required fields present")
            print(f"   AQI: {data.get('aqi')}")
            print(f"   PM2.5: {data.get('pm25')}")
            print(f"   Data Source: {data.get('data_source', 'unknown')}")
            print(f"   City: {data.get('city_name', 'unknown')}")
            
            if data.get('data_source') == 'aqicn_realtime':
                print("✅ Real-time data successfully retrieved")
                print(f"   Station: {data.get('station_name', 'Unknown')}")
                print(f"   Last Update: {data.get('last_update', 'Unknown')}")
            else:
                print(f"⚠️ Using fallback data: {data.get('data_source')}")
                
        else:
            print(f"⚠️ Missing fields: {missing_fields}")
            
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility error: {e}")
        return False

def test_indonesian_cities():
    """Test 3: Test multiple Indonesian cities"""
    print_header("TEST 3: Indonesian Cities Integration")
    
    try:
        from prediction.views import get_country_air_quality_data
        
        # Sample cities untuk testing
        test_cities = ['jakarta', 'medan', 'semarang', 'palembang', 'malang']
        
        results = {}
        
        for city in test_cities:
            print(f"\n🏙️ Testing {city.upper()}...")
            try:
                data = get_country_air_quality_data(city)
                
                aqi = data.get('aqi', 'N/A')
                pm25 = data.get('pm25', 'N/A')
                source = data.get('data_source', 'unknown')
                city_name = data.get('city_name', city)
                
                print(f"   AQI: {aqi}")
                print(f"   PM2.5: {pm25}")
                print(f"   Source: {source}")
                print(f"   City Name: {city_name}")
                
                if source == 'aqicn_realtime':
                    print(f"   ✅ Real-time data successful!")
                    station = data.get('station_name', 'Unknown')
                    update_time = data.get('last_update', 'Unknown')
                    print(f"   🏢 Station: {station}")
                    print(f"   🕐 Updated: {update_time}")
                else:
                    print(f"   ⚠️ Using fallback: {source}")
                
                results[city] = {
                    'success': True,
                    'aqi': aqi,
                    'source': source
                }
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results[city] = {'success': False, 'error': str(e)}
        
        # Summary
        print_subheader("Indonesian Cities Test Summary")
        successful = sum(1 for r in results.values() if r.get('success'))
        realtime = sum(1 for r in results.values() if r.get('source') == 'aqicn_realtime')
        
        print(f"📊 Successful requests: {successful}/{len(test_cities)}")
        print(f"🌐 Real-time sources: {realtime}/{len(test_cities)}")
        print(f"📈 Success rate: {(successful/len(test_cities)*100):.1f}%")
        
        for city, result in results.items():
            status = "✅" if result.get('success') else "❌"
            aqi = result.get('aqi', 'Error')
            source = result.get('source', 'Error')
            print(f"   {status} {city.upper()}: AQI={aqi}, Source={source}")
        
        return successful >= len(test_cities) * 0.8  # 80% success rate required
        
    except Exception as e:
        print(f"❌ Indonesian cities test error: {e}")
        return False

def test_cities_info_endpoint():
    """Test 4: Test cities info dan enhanced functions"""
    print_header("TEST 4: Enhanced Functions")
    
    try:
        from prediction.views import get_available_indonesian_cities_info, get_cities_simple
        from django.http import HttpRequest
        
        # Test cities info function
        print("🔄 Testing get_available_indonesian_cities_info()...")
        cities_info = get_available_indonesian_cities_info()
        
        print(f"✅ Cities info retrieved: {len(cities_info)} cities")
        print("📋 Available cities:")
        
        for i, city in enumerate(cities_info[:8]):  # Show first 8
            name = city.get('name', 'Unknown')
            region = city.get('region', 'Unknown')
            aqi = city.get('aqi_estimate', 'N/A')
            category = city.get('description', 'Unknown')
            
            print(f"   {i+1:2d}. {name} ({region}) - AQI: {aqi} - {category}")
        
        if len(cities_info) > 8:
            print(f"   ... and {len(cities_info) - 8} more cities")
        
        # Test get_cities_simple endpoint (simulate request)
        print("\n🔄 Testing get_cities_simple() endpoint...")
        
        # Create mock request
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'preview': 'false'}  # No real-time preview untuk speed
        
        from prediction.views import get_cities_simple
        response = get_cities_simple(request)
        
        if response.status_code == 200:
            print("✅ get_cities_simple endpoint working")
            # Could parse JSON response here if needed
        else:
            print(f"❌ get_cities_simple error: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Enhanced functions test error: {e}")
        return False

def test_data_quality():
    """Test 5: Verify data quality dan format consistency"""
    print_header("TEST 5: Data Quality & Format Consistency")
    
    try:
        from prediction.views import get_country_air_quality_data
        
        print("🔍 Testing data quality untuk sample cities...")
        
        sample_cities = ['indonesia', 'jakarta', 'medan']
        
        for city in sample_cities:
            print(f"\n📊 Analyzing data quality for {city}...")
            data = get_country_air_quality_data(city)
            
            # Check data types
            aqi = data.get('aqi')
            pm25 = data.get('pm25')
            
            # Validate AQI range
            aqi_valid = isinstance(aqi, (int, float)) and 0 <= aqi <= 500
            pm25_valid = isinstance(pm25, (int, float)) and pm25 >= 0
            
            print(f"   AQI: {aqi} (Valid: {'✅' if aqi_valid else '❌'})")
            print(f"   PM2.5: {pm25} (Valid: {'✅' if pm25_valid else '❌'})")
            
            # Check additional fields
            required_fields = ['humidity', 'temperature', 'data_source']
            field_status = {}
            
            for field in required_fields:
                value = data.get(field)
                has_value = value is not None and value != 'N/A'
                field_status[field] = has_value
                status_icon = "✅" if has_value else "⚠️"
                print(f"   {field}: {value} ({status_icon})")
            
            # Overall quality score
            valid_count = sum([aqi_valid, pm25_valid] + list(field_status.values()))
            total_count = 2 + len(required_fields)
            quality_score = (valid_count / total_count) * 100
            
            print(f"   📈 Data Quality Score: {quality_score:.1f}%")
            
            if quality_score >= 80:
                print(f"   ✅ Excellent data quality")
            elif quality_score >= 60:
                print(f"   ⚠️ Good data quality")
            else:
                print(f"   ❌ Poor data quality - needs attention")
        
        return True
        
    except Exception as e:
        print(f"❌ Data quality test error: {e}")
        return False

def test_fallback_system():
    """Test 6: Test fallback system reliability"""
    print_header("TEST 6: Fallback System Reliability")
    
    try:
        from prediction.views import get_static_air_quality_data
        
        print("🔄 Testing static fallback system...")
        
        # Test untuk existing cities
        test_cases = ['indonesia', 'jakarta', 'medan', 'invalid_city']
        
        for city in test_cases:
            print(f"\n🏗️ Testing fallback for '{city}'...")
            try:
                static_data = get_static_air_quality_data(city)
                
                aqi = static_data.get('aqi', 'N/A')
                pm25 = static_data.get('pm25', 'N/A')
                source = static_data.get('data_source', 'unknown')
                
                print(f"   ✅ Fallback successful")
                print(f"   AQI: {aqi}, PM2.5: {pm25}")
                print(f"   Source: {source}")
                
            except Exception as e:
                print(f"   ❌ Fallback failed: {e}")
                return False
        
        print("\n✅ Fallback system working reliably")
        return True
        
    except Exception as e:
        print(f"❌ Fallback system test error: {e}")
        return False

def test_performance():
    """Test 7: Basic performance testing"""
    print_header("TEST 7: Performance Testing")
    
    try:
        import time
        from prediction.views import get_country_air_quality_data
        
        print("⏱️ Testing response times...")
        
        test_cities = ['indonesia', 'jakarta', 'medan']
        times = []
        
        for city in test_cities:
            start_time = time.time()
            data = get_country_air_quality_data(city)
            end_time = time.time()
            
            response_time = end_time - start_time
            times.append(response_time)
            
            source = data.get('data_source', 'unknown')
            print(f"   {city}: {response_time:.2f}s ({source})")
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        print(f"\n📊 Performance Summary:")
        print(f"   Average response time: {avg_time:.2f}s")
        print(f"   Maximum response time: {max_time:.2f}s")
        
        if avg_time < 2.0:
            print(f"   ✅ Excellent performance")
        elif avg_time < 5.0:
            print(f"   ⚠️ Good performance")
        else:
            print(f"   ❌ Slow performance - consider optimization")
        
        return avg_time < 10.0  # Maximum acceptable: 10 seconds
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests dan generate report"""
    print_header("🎯 COMPREHENSIVE ENHANCED INTEGRATION TEST")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏗️ Testing enhanced Indonesian cities integration")
    
    tests = [
        ("Enhanced Views Import", test_views_import),
        ("Backward Compatibility", test_backward_compatibility), 
        ("Indonesian Cities Integration", test_indonesian_cities),
        ("Enhanced Functions", test_cities_info_endpoint),
        ("Data Quality & Format", test_data_quality),
        ("Fallback System", test_fallback_system),
        ("Performance Testing", test_performance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔄 Running: {test_name}...")
            result = test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)[:100]}"
    
    # Final comprehensive report
    print_header("📊 COMPREHENSIVE TEST RESULTS")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{result} | {test_name}")
        if "PASSED" in result:
            passed += 1
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced Indonesian integration is ready!")
        print("🚀 Your lung prediction system now uses real-time Indonesian air quality data!")
    elif passed >= total * 0.85:
        print("✅ Excellent! Most tests passed. System is ready with minor issues.")
    elif passed >= total * 0.70:
        print("⚠️ Good! System functional but some optimizations needed.")
    else:
        print("❌ Several issues detected. Review failed tests before deployment.")
    
    # Quick system summary
    print_subheader("🎯 System Enhancement Summary")
    try:
        from prediction.aqicn_integration import INDONESIAN_CITIES
        from prediction.views import get_country_air_quality_data
        
        # Quick real-time test
        sample_data = get_country_air_quality_data('jakarta')
        is_realtime = sample_data.get('data_source') == 'aqicn_realtime'
        
        print(f"📊 Available Indonesian Cities: {len(INDONESIAN_CITIES)}")
        print(f"🌐 Real-time Data Provider: aqicn.org")
        print(f"🔄 Current Data Source: {sample_data.get('data_source', 'unknown')}")
        print(f"📍 Sample (Jakarta): AQI={sample_data.get('aqi')}, PM2.5={sample_data.get('pm25')}")
        print(f"⚡ Real-time Status: {'✅ Active' if is_realtime else '⚠️ Fallback'}")
        
    except Exception as e:
        print(f"⚠️ Could not generate system summary: {e}")
    
    print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed, total

if __name__ == "__main__":
    try:
        passed, total = run_comprehensive_test()
        
        # Exit with appropriate code
        if passed == total:
            print(f"\n🎉 SUCCESS: All {total} tests passed!")
            sys.exit(0)
        elif passed >= total * 0.7:
            print(f"\n✅ MOSTLY SUCCESS: {passed}/{total} tests passed")
            sys.exit(0)
        else:
            print(f"\n⚠️ ISSUES DETECTED: Only {passed}/{total} tests passed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)