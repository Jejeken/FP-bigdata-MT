# test_final.py - Final Integration Test

import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

def test_imports():
    """Test if all imports work"""
    print("=== Testing Imports ===")
    
    try:
        from prediction.ml_models import get_predictor
        print("✅ X-ray model import: OK")
    except Exception as e:
        print(f"❌ X-ray model import error: {e}")
        return False
    
    try:
        from prediction.logreg_model import get_logreg_predictor
        print("✅ LogReg model import: OK")
    except Exception as e:
        print(f"❌ LogReg model import error: {e}")
        return False
    
    return True

def test_models():
    """Test model loading"""
    print("\n=== Testing Model Loading ===")
    
    try:
        from prediction.ml_models import get_predictor
        predictor = get_predictor()
        print("✅ X-ray model loaded")
        print(f"   Classes: {predictor.class_names}")
    except Exception as e:
        print(f"❌ X-ray model error: {e}")
        return False
    
    try:
        from prediction.logreg_model import get_logreg_predictor
        logreg = get_logreg_predictor()
        print("✅ LogReg model loaded")
    except Exception as e:
        print(f"❌ LogReg model error: {e}")
        return False
    
    return True

def test_logreg_prediction():
    """Test LogReg prediction"""
    print("\n=== Testing LogReg Prediction ===")
    
    try:
        from prediction.logreg_model import get_logreg_predictor
        logreg = get_logreg_predictor()
        
        result = logreg.predict_risk('indonesia')
        print(f"✅ Indonesia prediction: {result['risk_level']}")
        
        return True
    except Exception as e:
        print(f"❌ LogReg prediction error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Final Integration Test\n")
    
    # Test 1: Imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test 2: Model loading
        models_ok = test_models()
        
        if models_ok:
            # Test 3: LogReg prediction
            logreg_ok = test_logreg_prediction()
            
            if logreg_ok:
                print("\n🎉 ALL TESTS PASSED!")
                print("\nReady for testing:")
                print("1. python manage.py runserver")
                print("2. Upload NORMAL X-ray image")
                print("3. Should see LogReg risk prediction")
            else:
                print("\n❌ LogReg prediction failed")
        else:
            print("\n❌ Model loading failed")
    else:
        print("\n❌ Import failed")
    
    print("\n" + "="*50)