# debug_xray.py - Debug X-ray model predictions

import os
import sys
import django
import numpy as np

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

from prediction.ml_models import get_predictor

def debug_model_predictions():
    """Debug model predictions to check class mapping"""
    print("=== Debugging X-ray Model Predictions ===\n")
    
    try:
        predictor = get_predictor()
        
        print("🔍 Model Information:")
        print(f"   Input size: {predictor.input_size}")
        print(f"   Class names: {predictor.class_names}")
        print(f"   Model output shape: {predictor.model.output_shape}")
        
        # Check if we can inspect the model's training
        model = predictor.model
        
        # Test with a sample image if available
        sample_image_path = "D:/SEM 6/Big Data dalam Kesehatan/final-project/gambar/sample_xrayN.jpeg"  # Update this path
        
        if os.path.exists(sample_image_path):
            print(f"\n🧪 Testing with sample image: {sample_image_path}")
            
            # Get raw predictions
            preprocessed = predictor.preprocess_image(sample_image_path)
            raw_predictions = model.predict(preprocessed, verbose=0)
            
            print(f"Raw predictions: {raw_predictions[0]}")
            print(f"Prediction shape: {raw_predictions.shape}")
            
            # Check each class probability
            for i, class_name in enumerate(predictor.class_names):
                prob = raw_predictions[0][i]
                print(f"   {class_name} (index {i}): {prob:.4f} ({prob*100:.1f}%)")
            
            # Check predicted class
            predicted_index = np.argmax(raw_predictions[0])
            predicted_class = predictor.class_names[predicted_index]
            confidence = raw_predictions[0][predicted_index]
            
            print(f"\nPredicted: {predicted_class} (index {predicted_index}) with confidence {confidence:.4f}")
            
            # Compare with your Colab results
            print("\n📋 Questions to verify:")
            print("1. Does the predicted class match your expectation?")
            print("2. Are the class names in the same order as your training?")
            print("3. Is the preprocessing the same as in Colab?")
            
        else:
            print(f"⚠️  Sample image not found at {sample_image_path}")
            print("Please provide a sample image for testing")
            
        return True
        
    except Exception as e:
        print(f"❌ Error debugging model: {e}")
        return False

def check_class_mapping():
    """Check if class mapping is correct"""
    print("\n=== Checking Class Mapping ===\n")
    
    # Possible class orders that might be different
    possible_orders = [
        ['NORMAL', 'COVID', 'PNEUMONIA', 'TUBERCULOSIS'],
        ['COVID', 'NORMAL', 'PNEUMONIA', 'TUBERCULOSIS'],
        ['NORMAL', 'PNEUMONIA', 'COVID', 'TUBERCULOSIS'],
        ['COVID', 'PNEUMONIA', 'NORMAL', 'TUBERCULOSIS'],
        # Add more combinations if needed
    ]
    
    print("🔄 Possible class orders:")
    for i, order in enumerate(possible_orders):
        print(f"   Option {i+1}: {order}")
    
    print("\n❓ To fix class mapping:")
    print("1. Check your Colab notebook - what was the class order during training?")
    print("2. Look at model.fit() or train_generator.class_indices")
    print("3. Update class_names in ml_models.py to match training order")

def suggest_fixes():
    """Suggest possible fixes"""
    print("\n=== Suggested Fixes ===\n")
    
    print("🔧 Fix 1: Update Class Names Order")
    print("   Update this line in ml_models.py:")
    print("   self.class_names = ['CORRECT', 'ORDER', 'FROM', 'TRAINING']")
    
    print("\n🔧 Fix 2: Check Preprocessing")
    print("   Ensure preprocessing matches your Colab:")
    print("   - Image resize method")
    print("   - Normalization (0-1 vs ImageNet)")
    print("   - Color channel order (RGB vs BGR)")
    
    print("\n🔧 Fix 3: Verify Model File")
    print("   - Is this the same model from Colab?")
    print("   - Did you save it correctly?")
    print("   - Try re-downloading from Colab")

if __name__ == "__main__":
    print("🔍 Debugging X-ray Model Issues\n")
    
    success = debug_model_predictions()
    
    if success:
        check_class_mapping()
        suggest_fixes()
        
        print("\n📝 Next Steps:")
        print("1. Compare class order with your Colab training")
        print("2. Update class_names in ml_models.py if needed")
        print("3. Test again with known images")
        print("4. Check preprocessing differences")
    
    print("\n" + "="*60)