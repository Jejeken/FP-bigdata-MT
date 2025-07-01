# prediction/logreg_model.py

import joblib
import numpy as np
import pandas as pd
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AirQualityRiskPredictor:
    """
    Handler for Air Quality Risk prediction using Logistic Regression
    """
    
    def __init__(self):
        self.model = None
        self.risk_classes = {
            0: 'Rendah',
            1: 'Sedang', 
            2: 'Tinggi'
        }
        self.load_model()
        self.setup_country_data()
    
    def load_model(self):
        """Load the trained logistic regression model"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'models', 'multiclass_model.joblib')
            
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info(f"LogReg model loaded successfully from {model_path}")
                print(f"✅ Logistic Regression model loaded successfully!")
                
                # Print model info if available
                if hasattr(self.model, 'classes_'):
                    print(f"   Model classes: {self.model.classes_}")
                if hasattr(self.model, 'n_features_in_'):
                    print(f"   Expected features: {self.model.n_features_in_}")
                    
            else:
                logger.error(f"LogReg model file not found at {model_path}")
                raise FileNotFoundError(f"LogReg model file not found at {model_path}")
                
        except Exception as e:
            logger.error(f"Error loading LogReg model: {str(e)}")
            raise e
    
    def setup_country_data(self):
        """Setup country-specific air quality data based on Excel analysis"""
        self.country_data = {
            'indonesia': {
                'name': 'Indonesia',
                'aqi': 154,
                'pm1': 39.60,
                'pm10': 75.52,
                'pm25': 67.92,
                'relative_humidity': 45.61,
                'temperature': 31.16,
                'um003': 10004.65,
                'avg_cases': 107163.2
            },
            'singapore': {
                'name': 'Singapore', 
                'aqi': 66,
                'pm1': 13.92,
                'pm10': 22.61,
                'pm25': 20.65,
                'relative_humidity': 62.57,
                'temperature': 29.60,
                'um003': 2734.58,
                'avg_cases': 2729.75
            },
            'australia': {
                'name': 'Australia',
                'aqi': 25,
                'pm1': 4.24,
                'pm10': 6.05,
                'pm25': 5.65,
                'relative_humidity': 51.29,
                'temperature': 16.16,
                'um003': 965.67,
                'avg_cases': 44974.0
            }
        }
        
        # Setup StandardScaler with training data statistics
        # These values are approximated from your training data
        self.setup_scaler()
        
        print("🌍 Country air quality data initialized:")
        for country_code, data in self.country_data.items():
            print(f"   {data['name']}: AQI {data['aqi']}, PM2.5 {data['pm25']:.1f}")
    
    def setup_scaler(self):
        """Setup StandardScaler with approximate training statistics"""
        # Approximate statistics from your training data
        # You should replace these with actual values from your Colab training
        
        # Training data statistics (mean and std for each feature)
        # Features: [pm1, pm10, pm25, humidity, temperature, um003]
        self.feature_means = np.array([24.5, 41.8, 37.9, 53.2, 25.8, 5200.0])  # Approximate means
        self.feature_stds = np.array([18.2, 32.1, 29.8, 10.5, 7.2, 4800.0])   # Approximate stds
        
        print("📊 Using approximate StandardScaler statistics:")
        print(f"   Means: {self.feature_means}")
        print(f"   Stds: {self.feature_stds}")
        print("⚠️  For best results, use exact scaler from your Colab training!")
    
    def scale_features(self, features):
        """Apply StandardScaler transformation"""
        # StandardScaler formula: (x - mean) / std
        scaled_features = (features - self.feature_means) / self.feature_stds
        return scaled_features
    
    def get_country_air_quality(self, country_code):
        """Get air quality data for specified country"""
        if country_code.lower() in self.country_data:
            return self.country_data[country_code.lower()]
        else:
            logger.warning(f"Country {country_code} not found, using Indonesia as default")
            return self.country_data['indonesia']
    
    def prepare_features(self, country_data):
        """
        Prepare feature array for model prediction with StandardScaler
        """
        try:
            # Extract features in the same order as training data
            raw_features = np.array([
                country_data['pm1'],                    # parameter1 (pm1)
                country_data['pm10'],                   # parameter2 (pm10) 
                country_data['pm25'],                   # parameter3 (pm25)
                country_data['relative_humidity'],      # parameter4 (relativehumidity)
                country_data['temperature'],            # parameter5 (temperature)
                country_data['um003']                   # parameter6 (um003)
            ]).reshape(1, -1)
            
            print(f"🔧 Raw features: {raw_features[0]}")
            
            # Apply StandardScaler transformation (CRITICAL FIX!)
            scaled_features = self.scale_features(raw_features)
            
            print(f"🔧 Scaled features: {scaled_features[0]}")
            print(f"   Scaled PM1: {scaled_features[0][0]:.2f}")
            print(f"   Scaled PM10: {scaled_features[0][1]:.2f}")
            print(f"   Scaled PM2.5: {scaled_features[0][2]:.2f}")
            print(f"   Scaled Humidity: {scaled_features[0][3]:.2f}")
            print(f"   Scaled Temperature: {scaled_features[0][4]:.2f}")
            print(f"   Scaled UM003: {scaled_features[0][5]:.2f}")
            
            return scaled_features
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            raise e
    
    def predict_risk(self, country_code):
        """
        Predict air quality risk level for specified country
        
        Args:
            country_code: Country code ('indonesia', 'singapore', 'australia')
            
        Returns:
            dict: Risk prediction results
        """
        try:
            if self.model is None:
                raise ValueError("LogReg model not loaded")
            
            print(f"🔍 Predicting air quality risk for: {country_code}")
            
            # Get country data
            country_data = self.get_country_air_quality(country_code)
            
            # Prepare features
            features = self.prepare_features(country_data)
            
            # Make prediction
            print(f"🧠 Running LogReg prediction...")
            risk_prediction = self.model.predict(features)[0]
            risk_probabilities = self.model.predict_proba(features)[0]
            
            # Get risk level and confidence
            risk_level = self.risk_classes[risk_prediction]
            confidence = float(risk_probabilities[risk_prediction])
            
            print(f"📊 Risk Prediction Results:")
            print(f"   Predicted Risk Level: {risk_level} (class {risk_prediction})")
            print(f"   Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
            
            # Print all probabilities
            risk_probabilities_dict = {}
            for class_idx, prob in enumerate(risk_probabilities):
                class_name = self.risk_classes[class_idx]
                risk_probabilities_dict[class_name] = float(prob)
                print(f"   {class_name}: {prob:.3f} ({prob*100:.1f}%)")
            
            # Generate recommendations based on risk level
            recommendations = self.get_risk_recommendations(risk_level, country_data)
            
            result = {
                'country': country_data['name'],
                'country_code': country_code.lower(),
                'risk_level': risk_level,
                'risk_class': int(risk_prediction),
                'confidence': confidence,
                'confidence_percentage': round(confidence * 100, 1),
                'risk_probabilities': risk_probabilities_dict,
                'air_quality_data': {
                    'aqi': country_data['aqi'],
                    'pm25': country_data['pm25'],
                    'pm10': country_data['pm10'],
                    'pm1': country_data['pm1'],
                    'humidity': country_data['relative_humidity'],
                    'temperature': country_data['temperature'],
                    'um003': country_data['um003']
                },
                'recommendations': recommendations,
                'timeline_months': self.calculate_timeline(risk_level, confidence),
                'avg_cases_reference': country_data['avg_cases']
            }
            
            logger.info(f"Air quality risk prediction completed: {risk_level} for {country_data['name']}")
            return result
            
        except Exception as e:
            logger.error(f"Error during risk prediction: {str(e)}")
            print(f"❌ Risk prediction error: {str(e)}")
            raise e
    
    def get_risk_recommendations(self, risk_level, country_data):
        """Generate recommendations based on risk level"""
        
        base_recommendations = [
            'Monitor kualitas udara secara rutin',
            'Lakukan pemeriksaan kesehatan berkala',
            'Jaga pola hidup sehat dan olahraga teratur'
        ]
        
        if risk_level == 'Rendah':
            specific_recommendations = [
                'Kondisi udara relatif baik untuk aktivitas outdoor',
                'Tetap gunakan masker di area padat kendaraan',
                'Konsumsi makanan rich antioksidan sebagai pencegahan'
            ]
            timeline_advice = "Risiko rendah, pemeriksaan rutin 6-12 bulan sekali"
            
        elif risk_level == 'Sedang':
            specific_recommendations = [
                'Batasi aktivitas outdoor saat jam sibuk',
                'Gunakan masker N95 saat beraktivitas di luar',
                'Pasang air purifier di rumah dan kantor',
                'Tingkatkan asupan vitamin C dan antioksidan',
                'Avoid olahraga outdoor saat polusi tinggi'
            ]
            timeline_advice = "Risiko sedang, pemeriksaan kesehatan setiap 3-6 bulan"
            
        else:  # Tinggi
            specific_recommendations = [
                'Minimalisir aktivitas outdoor',
                'Selalu gunakan masker N95 atau N99 di luar rumah',
                'Gunakan air purifier dengan HEPA filter',
                'Pertimbangkan suplemen detoksifikasi',
                'Konsultasi dengan dokter untuk pemeriksaan paru',
                'Hindari area dengan traffic padat',
                'Monitor gejala pernapasan secara ketat'
            ]
            timeline_advice = "Risiko tinggi, pemeriksaan kesehatan setiap 1-3 bulan"
        
        return {
            'general': base_recommendations,
            'specific': specific_recommendations,
            'timeline_advice': timeline_advice,
            'aqi_context': f"AQI {country_data['aqi']} - {self.get_aqi_description(country_data['aqi'])}"
        }
    
    def get_aqi_description(self, aqi):
        """Get AQI description based on value"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def calculate_timeline(self, risk_level, confidence):
        """Calculate timeline for next checkup based on risk level"""
        base_months = {
            'Rendah': 12,
            'Sedang': 6,
            'Tinggi': 3
        }
        
        # Adjust based on confidence
        base = base_months.get(risk_level, 6)
        if confidence > 0.8:
            return base
        elif confidence > 0.6:
            return max(base - 1, 1)
        else:
            return max(base - 2, 1)

# Singleton instance
_logreg_predictor_instance = None

def get_logreg_predictor():
    """Get singleton instance of AirQualityRiskPredictor"""
    global _logreg_predictor_instance
    if _logreg_predictor_instance is None:
        _logreg_predictor_instance = AirQualityRiskPredictor()
    return _logreg_predictor_instance