# enhanced_risk_prediction.py
# Enhanced risk prediction dengan real-time AQI weighting
# Add this to prediction/views.py or create separate module

import numpy as np
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

def classify_aqi_risk(aqi_value: float) -> str:
    """
    Classify AQI value into risk levels
    
    Args:
        aqi_value: Real-time AQI value
        
    Returns:
        Risk level: 'Rendah', 'Sedang', or 'Tinggi'
    """
    if aqi_value < 100:
        return 'Rendah'
    elif aqi_value <= 150:
        return 'Sedang'
    else:  # aqi_value > 150
        return 'Tinggi'

def convert_aqi_risk_to_probabilities(aqi_risk: str) -> Dict[str, float]:
    """
    Convert AQI risk classification to probability distribution
    
    Args:
        aqi_risk: 'Rendah', 'Sedang', or 'Tinggi'
        
    Returns:
        Probability distribution for each risk level
    """
    # Strong probability distribution based on AQI
    if aqi_risk == 'Rendah':
        return {
            'Rendah': 0.85,   # Very confident
            'Sedang': 0.13,   # Small chance
            'Tinggi': 0.02    # Very small chance
        }
    elif aqi_risk == 'Sedang':
        return {
            'Rendah': 0.25,   # Some chance
            'Sedang': 0.65,   # High confidence
            'Tinggi': 0.10    # Moderate chance
        }
    else:  # 'Tinggi'
        return {
            'Rendah': 0.05,   # Very small chance
            'Sedang': 0.20,   # Small chance  
            'Tinggi': 0.75    # High confidence
        }

def parse_logreg_probabilities(logreg_result: Dict) -> Dict[str, float]:
    """
    Parse LogReg probabilities from existing model output
    
    Args:
        logreg_result: Current LogReg model output
        
    Returns:
        Standardized probability distribution
    """
    try:
        # Extract probabilities from logreg_details if available
        if 'logreg_details' in logreg_result:
            details = logreg_result['logreg_details']
            
            # Look for probability data in various possible formats
            if 'probabilities' in details:
                probs = details['probabilities']
                return {
                    'Rendah': probs.get('Rendah', probs.get(0, 0.0)),
                    'Sedang': probs.get('Sedang', probs.get(1, 0.0)),
                    'Tinggi': probs.get('Tinggi', probs.get(2, 0.0))
                }
            
            # Fallback: Create probabilities based on predicted risk level
            risk_level = logreg_result.get('risk_level', 'Sedang')
            confidence = logreg_result.get('confidence', 0.5)
            
            if risk_level == 'Rendah':
                return {
                    'Rendah': confidence,
                    'Sedang': (1 - confidence) * 0.7,
                    'Tinggi': (1 - confidence) * 0.3
                }
            elif risk_level == 'Sedang':
                return {
                    'Rendah': (1 - confidence) * 0.4,
                    'Sedang': confidence,
                    'Tinggi': (1 - confidence) * 0.6
                }
            else:  # 'Tinggi'
                return {
                    'Rendah': (1 - confidence) * 0.2,
                    'Sedang': (1 - confidence) * 0.3,
                    'Tinggi': confidence
                }
        
        # Ultimate fallback
        return {
            'Rendah': 0.33,
            'Sedang': 0.34,
            'Tinggi': 0.33
        }
        
    except Exception as e:
        logger.error(f"Error parsing LogReg probabilities: {e}")
        return {
            'Rendah': 0.33,
            'Sedang': 0.34,
            'Tinggi': 0.33
        }

def combine_predictions(
    logreg_probs: Dict[str, float], 
    aqi_probs: Dict[str, float],
    aqi_weight: float = 0.85
) -> Dict[str, float]:
    """
    Combine LogReg and AQI predictions with weighted average
    
    Args:
        logreg_probs: LogReg probability distribution
        aqi_probs: AQI-based probability distribution  
        aqi_weight: Weight for AQI (0.8-0.9 as requested)
        
    Returns:
        Combined probability distribution
    """
    logreg_weight = 1.0 - aqi_weight
    
    combined_probs = {}
    for risk_level in ['Rendah', 'Sedang', 'Tinggi']:
        combined_probs[risk_level] = (
            logreg_probs[risk_level] * logreg_weight + 
            aqi_probs[risk_level] * aqi_weight
        )
    
    return combined_probs

def get_final_prediction(combined_probs: Dict[str, float]) -> Tuple[str, float]:
    """
    Get final risk level and confidence from combined probabilities
    
    Args:
        combined_probs: Combined probability distribution
        
    Returns:
        Tuple of (risk_level, confidence)
    """
    # Find highest probability
    max_risk = max(combined_probs, key=combined_probs.get)
    max_confidence = combined_probs[max_risk]
    
    return max_risk, max_confidence

def calculate_enhanced_confidence(
    aqi_value: float,
    aqi_data_source: str,
    logreg_confidence: float,
    aqi_logreg_consistency: float
) -> Dict[str, float]:
    """
    Calculate enhanced confidence metrics
    
    Args:
        aqi_value: Real-time AQI value
        aqi_data_source: Source of AQI data (aqicn_realtime, etc.)
        logreg_confidence: Original LogReg confidence
        aqi_logreg_consistency: How consistent AQI and LogReg predictions are
        
    Returns:
        Enhanced confidence breakdown
    """
    # Base confidence from data source quality
    if aqi_data_source == 'aqicn_realtime':
        data_quality_score = 0.95
    elif 'static_indonesian_fallback' in aqi_data_source:
        data_quality_score = 0.75
    else:
        data_quality_score = 0.60
    
    # AQI confidence based on value range (more confident at extremes)
    if aqi_value < 50 or aqi_value > 200:
        aqi_confidence = 0.90  # Very confident at extremes
    elif aqi_value < 80 or aqi_value > 150:
        aqi_confidence = 0.85  # Confident
    else:
        aqi_confidence = 0.75  # Moderate confidence in middle ranges
    
    # Combined confidence
    final_confidence = (
        data_quality_score * 0.3 +
        aqi_confidence * 0.4 +
        logreg_confidence * 0.2 +
        aqi_logreg_consistency * 0.1
    )
    
    return {
        'final_confidence': min(final_confidence, 1.0),
        'data_quality': data_quality_score,
        'aqi_confidence': aqi_confidence,
        'logreg_confidence': logreg_confidence,
        'consistency_score': aqi_logreg_consistency
    }

def enhanced_risk_prediction(
    logreg_result: Dict,
    air_quality_data: Dict,
    aqi_weight: float = 0.85
) -> Dict:
    """
    Main function: Enhanced risk prediction dengan real-time AQI weighting
    
    Args:
        logreg_result: Original LogReg model result
        air_quality_data: Real-time air quality data
        aqi_weight: Weight for AQI influence (0.8-0.9)
        
    Returns:
        Enhanced prediction result
    """
    try:
        # Step 1: Get real-time AQI value
        aqi_value = air_quality_data.get('aqi', 100)
        aqi_data_source = air_quality_data.get('data_source', 'unknown')
        
        logger.info(f"🌍 Real-time AQI: {aqi_value} (source: {aqi_data_source})")
        
        # Step 2: Classify AQI into risk level
        aqi_risk = classify_aqi_risk(aqi_value)
        aqi_probs = convert_aqi_risk_to_probabilities(aqi_risk)
        
        logger.info(f"📊 AQI Risk Classification: {aqi_risk}")
        logger.info(f"📈 AQI Probabilities: {aqi_probs}")
        
        # Step 3: Parse LogReg probabilities
        logreg_probs = parse_logreg_probabilities(logreg_result)
        original_logreg_confidence = logreg_result.get('confidence', 0.5)
        
        logger.info(f"🤖 LogReg Probabilities: {logreg_probs}")
        
        # Step 4: Calculate consistency between AQI and LogReg
        logreg_risk = logreg_result.get('risk_level', 'Sedang')
        consistency_score = 1.0 if aqi_risk == logreg_risk else 0.5
        
        # Step 5: Combine predictions dengan weighting
        combined_probs = combine_predictions(logreg_probs, aqi_probs, aqi_weight)
        final_risk, final_confidence = get_final_prediction(combined_probs)
        
        logger.info(f"🎯 Combined Probabilities: {combined_probs}")
        logger.info(f"🏆 Final Prediction: {final_risk} ({final_confidence:.3f})")
        
        # Step 6: Calculate enhanced confidence
        enhanced_confidence_breakdown = calculate_enhanced_confidence(
            aqi_value, aqi_data_source, original_logreg_confidence, consistency_score
        )
        
        # Step 7: Build enhanced result
        enhanced_result = {
            # Core prediction
            'risk_level': final_risk,
            'confidence': enhanced_confidence_breakdown['final_confidence'],
            'confidence_percentage': round(enhanced_confidence_breakdown['final_confidence'] * 100, 1),
            
            # Enhanced details
            'enhancement_details': {
                'aqi_value': aqi_value,
                'aqi_risk_classification': aqi_risk,
                'aqi_weight_used': aqi_weight,
                'logreg_weight_used': 1.0 - aqi_weight,
                'data_source': aqi_data_source,
                'consistency_score': consistency_score
            },
            
            # Probability breakdown
            'probability_breakdown': {
                'final_probabilities': {
                    'Rendah': round(combined_probs['Rendah'] * 100, 1),
                    'Sedang': round(combined_probs['Sedang'] * 100, 1),
                    'Tinggi': round(combined_probs['Tinggi'] * 100, 1)
                },
                'logreg_probabilities': {
                    'Rendah': round(logreg_probs['Rendah'] * 100, 1),
                    'Sedang': round(logreg_probs['Sedang'] * 100, 1),
                    'Tinggi': round(logreg_probs['Tinggi'] * 100, 1)
                },
                'aqi_probabilities': {
                    'Rendah': round(aqi_probs['Rendah'] * 100, 1),
                    'Sedang': round(aqi_probs['Sedang'] * 100, 1),
                    'Tinggi': round(aqi_probs['Tinggi'] * 100, 1)
                }
            },
            
            # Confidence breakdown
            'confidence_breakdown': enhanced_confidence_breakdown,
            
            # Original data for reference
            'original_logreg': logreg_result,
            'used_realtime_data': aqi_data_source == 'aqicn_realtime',
            'air_quality_city': air_quality_data.get('city_name', 'Unknown'),
            'air_quality_station': air_quality_data.get('station_name', 'Unknown'),
            
            # Enhanced timeline based on risk level
            'timeline_months': get_enhanced_timeline(final_risk, aqi_value),
            
            # Enhanced recommendations
            'recommendations': get_enhanced_recommendations(final_risk, aqi_value, aqi_data_source)
        }
        
        logger.info(f"✅ Enhanced risk prediction completed successfully")
        return enhanced_result
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced risk prediction: {e}")
        # Fallback to original prediction
        return logreg_result

def get_enhanced_timeline(risk_level: str, aqi_value: float) -> int:
    """Get enhanced timeline based on risk and AQI"""
    base_timeline = {
        'Rendah': 12,    # 12 months
        'Sedang': 6,     # 6 months  
        'Tinggi': 3      # 3 months
    }
    
    timeline = base_timeline.get(risk_level, 6)
    
    # Adjust based on AQI severity
    if aqi_value > 200:  # Very high AQI
        timeline = max(timeline - 2, 1)  # More urgent
    elif aqi_value < 50:  # Very good AQI
        timeline = timeline + 3  # Less urgent
    
    return timeline

def get_enhanced_recommendations(risk_level: str, aqi_value: float, data_source: str) -> list:
    """Get enhanced recommendations based on risk and real-time AQI"""
    base_recommendations = {
        'Rendah': [
            'Lakukan pemeriksaan rutin tahunan',
            'Jaga pola hidup sehat dan olahraga teratur',
            'Konsumsi makanan bergizi dan perbanyak sayuran',
            'Hindari paparan asap rokok dan polutan'
        ],
        'Sedang': [
            'Lakukan pemeriksaan kesehatan setiap 6 bulan',
            'Gunakan masker saat beraktivitas di luar ruangan',
            'Perhatikan kualitas udara harian di aplikasi',
            'Konsultasi dengan dokter untuk pemeriksaan lanjutan'
        ],
        'Tinggi': [
            'Pemeriksaan medis segera dan berkala setiap 3 bulan',
            'Batasi aktivitas luar ruangan saat AQI tinggi',
            'Gunakan air purifier di rumah dan kantor',
            'Konsultasi dengan spesialis paru untuk tindakan preventif'
        ]
    }
    
    recommendations = base_recommendations.get(risk_level, base_recommendations['Sedang']).copy()
    
    # Add AQI-specific recommendations
    if aqi_value > 150:
        recommendations.extend([
            f'AQI saat ini {aqi_value} (Tidak Sehat) - hindari aktivitas outdoor',
            'Gunakan masker N95 ketika harus keluar rumah'
        ])
    elif aqi_value > 100:
        recommendations.append(f'AQI saat ini {aqi_value} (Sedang) - batasi olahraga outdoor')
    
    # Add data source info
    if data_source == 'aqicn_realtime':
        recommendations.append('Data kualitas udara real-time - pantau update harian')
    else:
        recommendations.append('Gunakan aplikasi kualitas udara untuk data terkini')
    
    return recommendations[:7]  # Limit to 7 recommendations

# Example usage and testing function
def test_enhanced_prediction():
    """Test function untuk enhanced prediction"""
    
    # Mock data for testing
    mock_logreg_result = {
        'risk_level': 'Sedang',
        'confidence': 0.65,
        'timeline_months': 6,
        'logreg_details': {
            'probabilities': {
                'Rendah': 0.25,
                'Sedang': 0.65,
                'Tinggi': 0.10
            }
        }
    }
    
    mock_air_quality_data = {
        'aqi': 135,
        'pm25': 55.5,
        'data_source': 'aqicn_realtime',
        'city_name': 'jakarta',
        'station_name': 'Kemayoran, Indonesia'
    }
    
    print("🧪 Testing Enhanced Risk Prediction")
    print("="*50)
    
    result = enhanced_risk_prediction(mock_logreg_result, mock_air_quality_data)
    
    print(f"Original LogReg: {mock_logreg_result['risk_level']} ({mock_logreg_result['confidence']:.3f})")
    print(f"Real-time AQI: {mock_air_quality_data['aqi']}")
    print(f"Enhanced Result: {result['risk_level']} ({result['confidence']:.3f})")
    print(f"Final Probabilities: {result['probability_breakdown']['final_probabilities']}")
    
    return result

if __name__ == "__main__":
    test_enhanced_prediction()