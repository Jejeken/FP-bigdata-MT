# test_new_model.py
# Script untuk test model ResNet yang baru

import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lung_prediction_system.settings')
django.setup()

import tensorflow as tf
import numpy as np
from prediction.ml_models import XRayPredictor

def inspect_new_model():
    """Inspect the new ResNet model structure"""
    print("=== Inspecting New ResNet Model ===\n")
    
    try:
        # Load model directly first
        model_path = "models/model_xray.h5"
        model = tf.keras.models.load_model(model_path, compile=False)
        
        print(f"✅ Model loaded successfully!")
        print(f"📊 Model Summary:")
        print(f"   - Input shape: {model.input_shape}")
        print(f"   - Output shape: {model.output_shape}")
        print(f"   - Total layers: {len(model.layers)}")
        print(f"   - Total parameters: {model.count_params():,}")
        
        # Check if it's a ResNet architecture
        layer_names = [layer.name for layer in model.layers]
        is_resnet = any('res' in name.lower() for name in layer_names)
        print(f"   - ResNet architecture detected: {is_resnet}")
        
        # Print first and last few layers
        print(f"\n🏗️  Model Architecture:")
        print(f"   First layer: {model.layers[0].name} - {type(model.layers[0]).__name__}")
        print(f"   Last layer: {model.layers[-1].name} - {type(model.layers[-1]).__name__}")
        
        # Check output layer
        output_units = model.layers[-1].units if hasattr(model.layers[-1], 'units') else model.output_shape[-1]
        print(f"   Output units: {output_units}")
        
        # Test with random input
        input_shape = model.input_shape[1:]  # Remove batch dimension
        test_input = np.random.rand(1, *input_shape).astype(np.float32)
        
        print(f"\n🧪 Testing with random input shape: {test_input.shape}")
        predictions = model.predict(test_input, verbose=0)
        print(f"   Output shape: {predictions.shape}")
        print(f"   Sample predictions: {predictions[0]}")
        print(f"   Prediction sum: {np.sum(predictions[0]):.3f}")
        
        # Check if output is normalized (softmax)
        is_normalized = abs(np.sum(predictions[0]) - 1.0) < 0.01
        print(f"   Softmax normalized: {is_normalized}")
        
        return True, input_shape, output_units
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False, None, None

def test_with_predictor():
    """Test using the XRayPredictor class"""
    print("\n=== Testing with XRayPredictor Class ===\n")
    
    try:
        predictor = XRayPredictor()
        print("✅ XRayPredictor loaded successfully!")
        print(f"   Expected input size: {predictor.input_size}")
        print(f"   Class names: {predictor.class_names}")
        
        return True
    except Exception as e:
        print(f"❌ Error with XRayPredictor: {e}")
        return False

def suggest_updates(input_shape, output_units):
    """Suggest any updates needed based on model inspection"""
    print("\n=== Suggested Updates ===\n")
    
    if input_shape:
        height, width = input_shape[0], input_shape[1]
        print(f"📝 Input size should be: ({width}, {height})")
        
        if width != 400 or height != 400:
            print(f"⚠️  Input size changed from (400, 400) to ({width}, {height})")
            print(f"   Need to update ml_model.py input_size")
    
    if output_units:
        print(f"📝 Output units: {output_units}")
        
        if output_units == 4:
            print("✅ 4 classes detected - current class names should work")
        else:
            print(f"⚠️  {output_units} classes detected - need to update class names")
            
        suggested_classes = {
            2: ['NORMAL', 'ABNORMAL'],
            3: ['NORMAL', 'COVID', 'PNEUMONIA'],
            4: ['NORMAL', 'COVID', 'PNEUMONIA', 'TUBERCULOSIS'],
            5: ['NORMAL', 'COVID', 'PNEUMONIA', 'TUBERCULOSIS', 'LUNG_OPACITY']
        }
        
        if output_units in suggested_classes:
            print(f"   Suggested class names: {suggested_classes[output_units]}")

if __name__ == "__main__":
    print("🔍 Testing New ResNet X-Ray Model\n")
    
    # Step 1: Inspect model
    success, input_shape, output_units = inspect_new_model()
    
    if success:
        # Step 2: Test with predictor
        predictor_ok = test_with_predictor()
        
        # Step 3: Suggest updates
        suggest_updates(input_shape, output_units)
        
        if predictor_ok:
            print("\n🎉 Model integration looks good!")
            print("   Ready to test with actual images!")
        else:
            print("\n⚠️  Need to update XRayPredictor configuration")
    
    print("\n" + "="*50)