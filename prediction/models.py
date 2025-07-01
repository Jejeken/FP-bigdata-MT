# prediction/models.py

from django.db import models
from django.core.validators import FileExtensionValidator
import uuid
import os

def upload_to_xray(instance, filename):
    """Generate unique filename for uploaded X-ray images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', 'xrays', filename)

class City(models.Model):
    """Model for Indonesian cities with coordinates"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class AirQualityData(models.Model):
    """Model to store air quality data for cities"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='air_quality_data')
    aqi = models.IntegerField()  # Air Quality Index
    pm25 = models.FloatField()   # PM2.5 concentration
    pm10 = models.FloatField()   # PM10 concentration
    o3 = models.FloatField()     # Ozone concentration
    no2 = models.FloatField()    # Nitrogen dioxide concentration
    so2 = models.FloatField()    # Sulfur dioxide concentration
    co = models.FloatField()     # Carbon monoxide concentration
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Air Quality Data"
    
    def __str__(self):
        return f"{self.city.name} - AQI: {self.aqi} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

    @property
    def aqi_status(self):
        """Return AQI status based on value"""
        if self.aqi <= 50:
            return {'status': 'Good', 'color': '#48bb78'}
        elif self.aqi <= 100:
            return {'status': 'Moderate', 'color': '#ed8936'}
        elif self.aqi <= 150:
            return {'status': 'Unhealthy for Sensitive Groups', 'color': '#f56565'}
        elif self.aqi <= 200:
            return {'status': 'Unhealthy', 'color': '#c53030'}
        elif self.aqi <= 300:
            return {'status': 'Very Unhealthy', 'color': '#9c4221'}
        else:
            return {'status': 'Hazardous', 'color': '#742a2a'}

class XRayAnalysis(models.Model):
    """Model to store X-ray analysis results"""
    CLASSIFICATION_CHOICES = [
        ('normal', 'Normal'),
        ('covid', 'COVID-19'),
        ('pneumonia', 'Pneumonia'),
        ('tuberculosis', 'Tuberculosis'),
        ('lung_opacity', 'Lung Opacity'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    air_quality_data = models.ForeignKey(AirQualityData, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Image and analysis
    xray_image = models.ImageField(
        upload_to=upload_to_xray,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    # Prediction results
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES)
    confidence_score = models.FloatField()  # 0-1 confidence
    
    # Risk prediction (for normal cases)
    risk_score = models.IntegerField(null=True, blank=True)  # 0-100%
    timeline_months = models.IntegerField(null=True, blank=True)  # months
    
    # Treatment recommendation (for abnormal cases)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "X-Ray Analyses"
    
    def __str__(self):
        return f"{self.classification.upper()} - {self.city.name} ({self.created_at.strftime('%Y-%m-%d')})"
    
    @property
    def is_normal(self):
        return self.classification == 'normal'
    
    @property
    def confidence_percentage(self):
        return round(self.confidence_score * 100, 1)

class Recommendation(models.Model):
    """Model to store recommendations for each analysis"""
    RECOMMENDATION_TYPES = [
        ('prevention', 'Prevention'),
        ('immediate_action', 'Immediate Action'),
        ('medication', 'Medication'),
        ('follow_up', 'Follow Up'),
    ]
    
    analysis = models.ForeignKey(XRayAnalysis, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    text = models.TextField()
    priority = models.IntegerField(default=1)  # 1=highest, 5=lowest
    
    class Meta:
        ordering = ['priority', 'id']
    
    def __str__(self):
        return f"{self.get_recommendation_type_display()} - {self.text[:50]}..."

class PredictionLog(models.Model):
    """Model to log all prediction requests for monitoring"""
    analysis = models.OneToOneField(XRayAnalysis, on_delete=models.CASCADE)
    processing_time = models.FloatField()  # seconds
    model_version = models.CharField(max_length=50, default='v1.0')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Log for {self.analysis.id} - {self.processing_time:.2f}s"