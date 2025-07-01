# prediction/ml_model.py - UPDATED FOR NEW RESNET MODEL

import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class XRayPredictor:
    """
    Handler for X-Ray image classification using the trained ResNet model
    """
    
    def __init__(self):
        self.model = None
        # FIXED: Correct class mapping - COVID: 0, NORMAL: 1, PNEUMONIA: 2, TUBERCULOSIS: 3
        self.class_names = ['COVID', 'NORMAL', 'PNEUMONIA', 'TUBERCULOSIS']
        self.input_size = (224, 224)  # Will be auto-detected from model
        self.load_model()
    
    def load_model(self):
        """Load the trained model from file"""
        try:
            model_path = settings.MODEL_PATH
            if os.path.exists(model_path):
                print(f"🔄 Loading ResNet model from {model_path}")
                
                # Load model and suppress warnings
                self.model = tf.keras.models.load_model(model_path, compile=False)
                
                # Recompile the model to avoid warnings
                self.model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                logger.info(f"Model loaded successfully from {model_path}")
                print(f"✅ ResNet model loaded successfully!")
                print(f"📊 Model details:")
                print(f"   - Input shape: {self.model.input_shape}")
                print(f"   - Output shape: {self.model.output_shape}")
                print(f"   - Total parameters: {self.model.count_params():,}")
                
                # Auto-detect and update input size from model
                model_height = self.model.input_shape[1]
                model_width = self.model.input_shape[2]
                self.input_size = (model_width, model_height)
                print(f"   - Auto-detected input size: {self.input_size}")
                
                # Auto-detect number of classes
                output_units = self.model.output_shape[-1]
                print(f"   - Number of classes: {output_units}")
                
                # Adjust class names if needed
                if output_units != len(self.class_names):
                    print(f"⚠️  Model has {output_units} classes, but {len(self.class_names)} class names provided")
                    # You can update class_names here based on your model
                
            else:
                logger.error(f"Model file not found at {model_path}")
                raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise e
    
    def preprocess_image(self, image_path):
        """
        Preprocess the image for ResNet model prediction
        
        Args:
            image_path: Path to the image file
            
        Returns:
            preprocessed_image: Numpy array ready for prediction
        """
        try:
            print(f"🖼️  Preprocessing image: {image_path}")
            
            # Read image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot read image from {image_path}")
            
            print(f"   Original shape: {image.shape}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size
            image = cv2.resize(image, self.input_size, interpolation=cv2.INTER_AREA)
            print(f"   Resized to: {image.shape}")
            
            # Convert to float32 and normalize
            image = image.astype(np.float32)
            
            # ResNet typically uses ImageNet normalization
            # You might need to adjust this based on how your model was trained
            image = image / 255.0  # Basic normalization
            
            # Alternative: ImageNet normalization (uncomment if needed)
            # mean = np.array([0.485, 0.456, 0.406])
            # std = np.array([0.229, 0.224, 0.225])
            # image = (image - mean) / std
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            print(f"   Final shape: {image.shape}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise e
    
    def predict(self, image_path):
        """
        Make prediction on X-ray image using ResNet model
        
        Args:
            image_path: Path to the X-ray image
            
        Returns:
            dict: Prediction results containing classification and confidence
        """
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            print(f"🧠 Starting ResNet prediction for: {os.path.basename(image_path)}")
            
            # Preprocess image
            preprocessed_image = self.preprocess_image(image_path)
            
            print(f"🔄 Running model inference...")
            
            # Make prediction
            predictions = self.model.predict(preprocessed_image, verbose=0)
            print(f"✅ Prediction completed!")
            print(f"   Raw predictions shape: {predictions.shape}")
            print(f"   Raw predictions: {predictions[0]}")
            
            # Get predicted class and confidence
            predicted_class_index = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_index])
            predicted_class = self.class_names[predicted_class_index].lower()
            
            print(f"📊 Results:")
            print(f"   Predicted class: {predicted_class} (index: {predicted_class_index})")
            print(f"   Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
            
            # Get all class probabilities
            class_probabilities = {}
            for i, class_name in enumerate(self.class_names):
                prob = float(predictions[0][i])
                class_probabilities[class_name.lower()] = prob
                print(f"   {class_name}: {prob:.3f} ({prob*100:.1f}%)")
            
            result = {
                'classification': predicted_class,
                'confidence': confidence,
                'all_probabilities': class_probabilities,
                'raw_predictions': predictions[0].tolist(),
                'model_type': 'resnet'
            }
            
            logger.info(f"ResNet prediction completed: {predicted_class} with confidence {confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            print(f"❌ Prediction error: {str(e)}")
            raise e
    
    def get_risk_prediction(self, classification, confidence, air_quality_data):
        """
        Calculate risk prediction for normal cases using LogReg model
        """
        if classification.lower().strip() != 'normal':
            print(f"⚠️  Classification '{classification}' is not normal, skipping risk prediction")
            return None
        
        try:
            print(f"🔄 Starting risk prediction for NORMAL case...")
            
            # Import the LogReg predictor - FIXED import path
            try:
                from .logreg_model import get_logreg_predictor
                print(f"✅ LogReg module imported successfully")
            except ImportError as e:
                print(f"❌ LogReg import error: {e}")
                # Try alternative import
                try:
                    from prediction.logreg_model import get_logreg_predictor
                    print(f"✅ LogReg module imported with alternative path")
                except ImportError as e2:
                    print(f"❌ Alternative LogReg import also failed: {e2}")
                    return self._get_simple_risk_prediction(confidence, air_quality_data)
            
            # Get country code from air quality data
            country_code = air_quality_data.get('country_code', 'indonesia') if air_quality_data else 'indonesia'
            print(f"🌍 Using country code: {country_code}")
            
            # Get LogReg predictor and make prediction
            logreg_predictor = get_logreg_predictor()
            print(f"🤖 LogReg predictor loaded, making prediction...")
            
            risk_result = logreg_predictor.predict_risk(country_code)
            print(f"🎯 LogReg prediction completed!")
            
            # Convert LogReg result to format expected by frontend
            risk_score_mapping = {
                'Rendah': 25,
                'Sedang': 55, 
                'Tinggi': 85
            }
            
            risk_score = risk_score_mapping.get(risk_result['risk_level'], 50)
            timeline_months = risk_result['timeline_months']
            
            # Combine LogReg recommendations with X-ray confidence factor
            recommendations = risk_result['recommendations']['general'] + risk_result['recommendations']['specific']
            
            # Add X-ray confidence consideration
            if confidence < 0.8:
                recommendations.append('X-ray menunjukkan hasil normal dengan confidence rendah, pertimbangkan pemeriksaan ulang')
            
            final_result = {
                'risk_score': risk_score,
                'timeline_months': timeline_months,
                'risk_level': risk_result['risk_level'],
                'confidence': risk_result['confidence'],
                'confidence_percentage': round(risk_result['confidence'] * 100, 1),
                'logreg_details': risk_result,
                'recommendations': recommendations[:7],  # Limit to 7 recommendations for UI
                'factors': {
                    'logreg_risk_level': risk_result['risk_level'],
                    'air_quality_aqi': risk_result['air_quality_data']['aqi'],
                    'xray_confidence': confidence,
                    'country': risk_result['country']
                }
            }
            
            print(f"✅ Risk prediction successful: {risk_result['risk_level']} level")
            return final_result
            
        except Exception as e:
            print(f"❌ Error using LogReg for risk prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fallback to simple calculation if LogReg fails
            return self._get_simple_risk_prediction(confidence, air_quality_data)
    
    def _get_simple_risk_prediction(self, confidence, air_quality_data):
        """Fallback simple risk prediction if LogReg fails"""
        base_risk = 30
        
        # Simple AQI-based risk
        aqi = air_quality_data.get('aqi', 100) if air_quality_data else 100
        if aqi > 150:
            aqi_risk = 40
        elif aqi > 100:
            aqi_risk = 20
        else:
            aqi_risk = 10
        
        total_risk = min(base_risk + aqi_risk, 85)
        timeline_months = 12 if total_risk < 50 else 6
        
        return {
            'risk_score': int(total_risk),
            'timeline_months': timeline_months,
            'recommendations': [
                'Gunakan masker saat beraktivitas di luar ruangan',
                'Monitor kualitas udara secara rutin',
                'Lakukan pemeriksaan kesehatan berkala',
                'Konsumsi makanan rich antioksidan'
            ],
            'factors': {
                'fallback_mode': True,
                'base_risk': base_risk,
                'aqi_risk': aqi_risk
            }
        }
    
    def get_treatment_recommendation(self, classification, confidence):
        """Get treatment recommendations based on ResNet prediction"""
        if classification == 'normal':
            return None
        
        # Enhanced severity determination for ResNet
        if confidence > 0.95:
            severity = 'severe'
        elif confidence > 0.8:
            severity = 'moderate'
        else:
            severity = 'mild'
        
        # Same recommendations as before but with ResNet confidence consideration
        recommendations = {
            'covid': {
                'immediate_actions': [
                    'Isolasi mandiri segera untuk mencegah penyebaran',
                    'Konsultasi dengan dokter atau layanan telemedicine',
                    'Monitor saturasi oksigen dan suhu tubuh',
                    'Istirahat total dan hindari aktivitas berat'
                ],
                'medications': [
                    'Paracetamol untuk menurunkan demam',
                    'Vitamin C dan D dosis tinggi',
                    'Zinc supplement untuk meningkatkan imunitas',
                    'Obat batuk ekspektoran jika ada batuk berdahak'
                ],
                'follow_up': 'Kontrol dalam 3-5 hari atau segera jika sesak napas'
            },
            'pneumonia': {
                'immediate_actions': [
                    'Konsultasi segera dengan dokter spesialis paru',
                    'Pertimbangkan rawat inap jika kondisi berat',
                    'Monitor tanda vital secara rutin',
                    'Istirahat dan hindari paparan dingin'
                ],
                'medications': [
                    'Antibiotik sesuai resep dokter',
                    'Bronkodilator untuk melancarkan pernapasan',
                    'Mukolitik untuk mengencerkan dahak',
                    'Analgesik untuk mengurangi nyeri dada'
                ],
                'follow_up': 'Kontrol dalam 1-2 minggu atau jika gejala memburuk'
            },
            'tuberculosis': {
                'immediate_actions': [
                    'Konsultasi segera dengan dokter spesialis paru',
                    'Lakukan pemeriksaan sputum BTA',
                    'Isolasi untuk mencegah penularan',
                    'Tingkatkan asupan nutrisi dan istirahat'
                ],
                'medications': [
                    'OAT (Obat Anti Tuberkulosis) sesuai program DOTS',
                    'Vitamin B6 untuk mencegah efek samping OAT',
                    'Suplemen nutrisi untuk meningkatkan daya tahan',
                    'Ekspektoran untuk membantu pengeluaran dahak'
                ],
                'follow_up': 'Kontrol rutin setiap bulan selama masa pengobatan'
            }
        }
        
        default_recommendations = {
            'immediate_actions': [
                'Konsultasi dengan dokter spesialis paru',
                'Istirahat yang cukup',
                'Monitor gejala pernapasan',
                'Hindari paparan polusi udara'
            ],
            'medications': [
                'Sesuai anjuran dokter',
                'Vitamin untuk meningkatkan imunitas',
                'Obat pereda gejala jika diperlukan'
            ],
            'follow_up': 'Kontrol dalam 1-2 minggu'
        }
        
        treatment_rec = recommendations.get(classification, default_recommendations)
        treatment_rec['severity'] = severity.title()
        treatment_rec['model_confidence'] = confidence
        
        return treatment_rec

# Singleton instance
_predictor_instance = None

def get_predictor():
    """Get singleton instance of XRayPredictor"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = XRayPredictor()
    return _predictor_instance