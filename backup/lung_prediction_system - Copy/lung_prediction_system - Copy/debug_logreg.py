# debug_logreg.py - Debug LogReg Predictions

import os
import sys
import django
import numpy as np

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

def debug_logreg_predictions():
    """Debug LogReg predictions for all countries"""
    print("=== Debugging LogReg Predictions ===\n")
    
    try:
        from prediction.logreg_model import get_logreg_predictor
        
        predictor = get_logreg_predictor()
        
        # Test all 3 countries
        countries = ['indonesia', 'singapore', 'australia']
        
        print("🔍 Raw LogReg Model Info:")
        if hasattr(predictor.model, 'classes_'):
            print(f"   Model classes: {predictor.model.classes_}")
        if hasattr(predictor.model, 'coef_'):
            print(f"   Model coefficients shape: {predictor.model.coef_.shape}")
            print(f"   Feature importance (first few): {predictor.model.coef_[0][:3]}")
        
        print(f"\n📊 Country Data & Predictions:")
        print("-" * 80)
        
        for country in countries:
            print(f"\n🌍 {country.upper()}:")
            
            # Get country data
            country_data = predictor.get_country_air_quality(country)
            
            # Show input features
            features = predictor.prepare_features(country_data)
            print(f"   Input features: {features[0]}")
            print(f"   PM1: {features[0][0]:.2f}")
            print(f"   PM10: {features[0][1]:.2f}")
            print(f"   PM2.5: {features[0][2]:.2f}")
            print(f"   Humidity: {features[0][3]:.2f}%")
            print(f"   Temperature: {features[0][4]:.2f}°C")
            print(f"   UM003: {features[0][5]:.2f}")
            print(f"   AQI (reference): {country_data['aqi']}")
            
            # Get raw predictions
            raw_pred = predictor.model.predict(features)[0]
            raw_proba = predictor.model.predict_proba(features)[0]
            
            print(f"   Raw prediction: {raw_pred}")
            print(f"   Raw probabilities: {raw_proba}")
            
            # Show class probabilities
            for i, prob in enumerate(raw_proba):
                class_name = predictor.risk_classes[i]
                print(f"     Class {i} ({class_name}): {prob:.4f} ({prob*100:.1f}%)")
            
            # Final result
            result = predictor.predict_risk(country)
            print(f"   FINAL PREDICTION: {result['risk_level']}")
            print(f"   Confidence: {result['confidence']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debugging LogReg: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_training_data():
    """Analyze the original training data to understand class distribution"""
    print("\n=== Analyzing Training Data ===\n")
    
    # Based on Excel data you provided earlier
    training_data = [
        # Indonesia data
        {'country': 'Indonesia', 'pm1': 23.08, 'pm10': 42.76, 'pm25': 36.98, 'humidity': 53.54, 'temp': 30.63, 'um003': 4940.47, 'cases': 99130},
        {'country': 'Indonesia', 'pm1': 42.34, 'pm10': 81.14, 'pm25': 72.48, 'humidity': 43.07, 'temp': 31.32, 'um003': 10844.98, 'cases': 104638},
        {'country': 'Indonesia', 'pm1': 38.39, 'pm10': 75.01, 'pm25': 66.78, 'humidity': 44.01, 'temp': 31.19, 'um003': 9727.04, 'cases': 102609},
        {'country': 'Indonesia', 'pm1': 44.21, 'pm10': 83.39, 'pm25': 75.31, 'humidity': 42.82, 'temp': 31.27, 'um003': 11424.30, 'cases': 119734},
        {'country': 'Indonesia', 'pm1': 49.95, 'pm10': 95.32, 'pm25': 88.06, 'humidity': 44.59, 'temp': 31.36, 'um003': 13086.46, 'cases': 109705},
        
        # Australia data  
        {'country': 'Australia', 'pm1': 1.85, 'pm10': 2.98, 'pm25': 2.68, 'humidity': 50.18, 'temp': 16.74, 'um003': 534.10, 'cases': 17459},
        {'country': 'Australia', 'pm1': 4.25, 'pm10': 5.89, 'pm25': 5.57, 'humidity': 50.60, 'temp': 16.23, 'um003': 962.61, 'cases': 51727},
        {'country': 'Australia', 'pm1': 6.88, 'pm10': 9.57, 'pm25': 9.01, 'humidity': 50.99, 'temp': 15.23, 'um003': 1454.88, 'cases': 78768},
        {'country': 'Australia', 'pm1': 3.98, 'pm10': 5.75, 'pm25': 5.36, 'humidity': 53.39, 'temp': 16.44, 'um003': 911.09, 'cases': 31942},
        
        # Singapore data
        {'country': 'Singapore', 'pm1': 14.46, 'pm10': 23.75, 'pm25': 21.57, 'humidity': 72.70, 'temp': 30.32, 'um003': 2842.82, 'cases': 2121},
        {'country': 'Singapore', 'pm1': 15.18, 'pm10': 24.87, 'pm25': 22.60, 'humidity': 70.03, 'temp': 29.73, 'um003': 2995.69, 'cases': 2907},
        {'country': 'Singapore', 'pm1': 10.74, 'pm10': 16.69, 'pm25': 15.67, 'humidity': 52.74, 'temp': 29.56, 'um003': 2074.38, 'cases': 2674},
        {'country': 'Singapore', 'pm1': 15.30, 'pm10': 25.12, 'pm25': 22.75, 'humidity': 54.80, 'temp': 28.80, 'um003': 3025.43, 'cases': 3217}
    ]
    
    # Sort by cases to see class distribution
    all_cases = [row['cases'] for row in training_data]
    all_cases.sort()
    
    print("📊 Training Data Cases (sorted):")
    for i, cases in enumerate(all_cases):
        print(f"   {i+1:2d}. {cases:,} cases")
    
    # Calculate class boundaries (33.3% each)
    n_samples = len(all_cases)
    low_boundary = all_cases[n_samples // 3]
    high_boundary = all_cases[2 * n_samples // 3]
    
    print(f"\n🎯 Class Boundaries:")
    print(f"   Rendah (0): <= {low_boundary:,} cases")
    print(f"   Sedang (1): {low_boundary:,} < cases <= {high_boundary:,}")
    print(f"   Tinggi (2): > {high_boundary:,} cases")
    
    # Classify each country's average
    print(f"\n🌍 Expected Classifications:")
    countries_avg = {}
    for country in ['Indonesia', 'Australia', 'Singapore']:
        country_data = [row for row in training_data if row['country'] == country]
        avg_cases = sum(row['cases'] for row in country_data) / len(country_data)
        
        if avg_cases <= low_boundary:
            expected_class = "Rendah (0)"
        elif avg_cases <= high_boundary:
            expected_class = "Sedang (1)"
        else:
            expected_class = "Tinggi (2)"
        
        print(f"   {country}: {avg_cases:,.0f} cases → {expected_class}")
        countries_avg[country] = avg_cases
    
    return countries_avg

def suggest_fixes():
    """Suggest possible fixes"""
    print("\n=== Possible Issues & Fixes ===\n")
    
    print("🔧 Possible Issues:")
    print("1. Model was trained on case numbers, not AQI")
    print("2. Feature scaling might be different between training and prediction")
    print("3. Model might be overfitting to UM003 parameter")
    print("4. Class boundaries might not match actual risk levels")
    
    print("\n💡 Suggested Fixes:")
    print("1. Check if model was trained with feature scaling/normalization")
    print("2. Verify feature order matches training data")
    print("3. Consider retraining model with balanced classes")
    print("4. Add feature scaling to prediction pipeline")

if __name__ == "__main__":
    print("🔍 Debugging LogReg Always Predicting 'Tinggi'\n")
    
    # Step 1: Debug current predictions
    success = debug_logreg_predictions()
    
    if success:
        # Step 2: Analyze training data
        analyze_training_data()
        
        # Step 3: Suggest fixes
        suggest_fixes()
        
        print("\n📝 Next Steps:")
        print("1. Check if your LogReg model used feature scaling")
        print("2. Verify feature order in training vs prediction")
        print("3. Consider retraining with proper class distribution")
    
    print("\n" + "="*80)