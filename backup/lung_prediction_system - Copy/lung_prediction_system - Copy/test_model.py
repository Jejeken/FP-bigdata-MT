# test_model.py
# Letakkan file ini di root directory project Anda, sejajar dengan manage.py

import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

from prediction.ml_models import XRayPredictor

def test_model_loading():
    """Test if model can be loaded successfully"""
    print("Testing model loading...")
    
    try:
        predictor = XRayPredictor()
        print("✅ Model loaded successfully!")
        print(f"Model input shape: {predictor.model.input_shape}")
        print(f"Model output shape: {predictor.model.output_shape}")
        print(f"Expected input size: {predictor.input_size}")
        print(f"Class names: {predictor.class_names}")
        
        # Test if input size matches model
        expected_height = predictor.model.input_shape[1]
        expected_width = predictor.model.input_shape[2]
        actual_width, actual_height = predictor.input_size
        
        if expected_height == actual_height and expected_width == actual_width:
            print("✅ Input size matches model requirements!")
        else:
            print(f"⚠️  Input size mismatch - Model expects: {expected_height}x{expected_width}, Got: {actual_height}x{actual_width}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_image_preprocessing():
    """Test image preprocessing with a sample image"""
    print("\nTesting image preprocessing...")
    
    # Anda perlu meletakkan sample image untuk test
    sample_image_path = "D:/SEM 6/Big Data dalam Kesehatan/final-project/gambar/sample_xrayC104.jpeg"  # Ganti dengan path image test Anda
    
    if not os.path.exists(sample_image_path):
        print(f"❌ Sample image not found at {sample_image_path}")
        print("Please put a sample X-ray image and update the path")
        return False
    
    try:
        predictor = XRayPredictor()
        preprocessed = predictor.preprocess_image(sample_image_path)
        print(f"✅ Image preprocessing successful!")
        print(f"Preprocessed shape: {preprocessed.shape}")
        return True
    except Exception as e:
        print(f"❌ Error preprocessing image: {e}")
        return False

def test_prediction():
    """Test full prediction pipeline"""
    print("\nTesting prediction...")
    
    sample_image_path = "D:/SEM 6/Big Data dalam Kesehatan/final-project/gambar/sample_xrayC104.jpeg"  # Ganti dengan path image test Anda
    
    if not os.path.exists(sample_image_path):
        print(f"❌ Sample image not found at {sample_image_path}")
        return False
    
    try:
        predictor = XRayPredictor()
        result = predictor.predict(sample_image_path)
        
        print("✅ Prediction successful!")
        print(f"Classification: {result['classification']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"All probabilities: {result['all_probabilities']}")
        return True
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing X-Ray Model Integration ===\n")
    
    # Test 1: Model loading
    model_loaded = test_model_loading()
    
    if model_loaded:
        # Test 2: Image preprocessing 
        preprocessing_ok = test_image_preprocessing()
        
        if preprocessing_ok:
            # Test 3: Full prediction
            test_prediction()
    
    print("\n=== Test completed ===")