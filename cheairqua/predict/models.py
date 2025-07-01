from django.db import models
import os
from openaq import OpenAQ
import re
from typing import Union, Optional

API_KEY = os.getenv('OPENAQ_API_KEY', '2ad5c805534fabe02ef4baa9f0a374d502e9607b02ec080b8323dced2866b25e')
client = OpenAQ(api_key=API_KEY)

def air_quality(location_id):
    sensor_data = client.locations.sensors(location_id)
    
    client.close()
    return sensor_data


def extract_pm25_value(data: Union[str, object], debug: bool = False) -> Optional[float]:
    """
    Extract PM2.5 value from either string representation or SensorsResponse object
    """
    
    if debug:
        print(f"Data type: {type(data)}")
        print(f"Data (first 200 chars): {str(data)[:200]}...")
    
    # If it's already a string, use regex
    if isinstance(data, str):
        # Multiple patterns to try
        patterns = [
            r"name='pm25[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)",
            r"'name':\s*'pm25'.*?'value':\s*([0-9.]+)",
            r"pm25.*?value.*?([0-9]+\.?[0-9]*)",
            r"'value':\s*([0-9.]+).*?'pm25'",
            r"Sensor.*?pm25.*?value.*?([0-9]+\.?[0-9]*)"
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, data, re.DOTALL | re.IGNORECASE)
            if match:
                if debug:
                    print(f"Pattern {i+1} matched: {match.group(1)}")
                return float(match.group(1))
        
        if debug:
            print("No regex patterns matched")
        return None
    
    # If it's a SensorsResponse object, extract directly
    try:
        # Assuming it's a SensorsResponse object with results attribute
        if hasattr(data, 'results'):
            if debug:
                print(f"Found {len(data.results)} sensors")
            
            for i, sensor in enumerate(data.results):
                if debug:
                    sensor_name = getattr(sensor, 'name', 'Unknown')
                    param_name = getattr(getattr(sensor, 'parameter', None), 'name', 'Unknown') if hasattr(sensor, 'parameter') else 'Unknown'
                    print(f"Sensor {i}: name='{sensor_name}', parameter='{param_name}'")
                
                # Check if this is a PM2.5 sensor
                if (hasattr(sensor, 'parameter') and 
                    hasattr(sensor.parameter, 'name') and
                    sensor.parameter.name == 'pm25'):
                    
                    if (hasattr(sensor, 'latest') and 
                        hasattr(sensor.latest, 'value')):
                        value = sensor.latest.value
                        if debug:
                            print(f"Found PM2.5 sensor with value: {value}")
                        return float(value)
        
        # If direct attribute access fails, try string representation
        data_str = str(data)
        if debug:
            print("Falling back to string parsing...")
        
        # More comprehensive patterns for string representation
        patterns = [
            r"name='pm25[^']*'.*?latest=.*?'value':\s*([0-9.]+)",
            r"parameter.*?'name':\s*'pm25'.*?latest.*?'value':\s*([0-9.]+)",
            r"Sensor.*?pm25.*?latest.*?value.*?([0-9]+\.?[0-9]*)",
            r"'pm25'.*?'value':\s*([0-9.]+)"
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, data_str, re.DOTALL | re.IGNORECASE)
            if match:
                if debug:
                    print(f"String pattern {i+1} matched: {match.group(1)}")
                return float(match.group(1))
            
    except (AttributeError, ValueError, TypeError) as e:
        print(f"Error extracting PM2.5 value: {e}")
        return None
    
    if debug:
        print("No PM2.5 value found")
    return None


def extract_all_sensor_values(data: Union[str, object]) -> dict:
    """
    Extract all sensor values from the data
    """
    sensor_values = {}
    
    # If it's a SensorsResponse object, extract directly
    if hasattr(data, 'results'):
        try:
            for sensor in data.results:
                if (hasattr(sensor, 'parameter') and 
                    hasattr(sensor, 'latest') and
                    hasattr(sensor.latest, 'value')):
                    
                    param_name = sensor.parameter.name
                    param_units = getattr(sensor.parameter, 'units', '')
                    latest_value = sensor.latest.value
                    
                    sensor_values[f"{param_name}_{param_units}"] = float(latest_value)
            
            return sensor_values
            
        except (AttributeError, ValueError) as e:
            print(f"Error extracting sensor values: {e}")
    
    # Fallback to string parsing
    data_str = str(data)
    
    # Patterns for different sensor types
    patterns = {
        'pm25': r"name='pm25[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)",
        'pm10': r"name='pm10[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)",
        'pm1': r"name='pm1[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)",
        'temperature': r"name='temperature[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)",
        'relativehumidity': r"name='relativehumidity[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)",
        'um003': r"name='um003[^']*'.*?latest=\{[^}]*'value':\s*([0-9.]+)"
    }
    
    for sensor_type, pattern in patterns.items():
        match = re.search(pattern, data_str)
        if match:
            sensor_values[sensor_type] = float(match.group(1))
    
    return sensor_values

def calculate_aqi_pm25(pm25_concentration: Optional[float]) -> Optional[dict]:
    """
    Calculates the US EPA Air Quality Index (AQI) for PM2.5.
    Returns a dictionary with AQI value, category, and raw PM2.5 value.
    """
    if pm25_concentration is None or pm25_concentration < 0:
        return None

    c = int(pm25_concentration * 10) / 10.0

    if 0.0 <= c <= 12.0:
        i_low, i_high, c_low, c_high, category = 0, 50, 0.0, 12.0, "Baik"
    elif 12.1 <= c <= 35.4:
        i_low, i_high, c_low, c_high, category = 51, 100, 12.1, 35.4, "Sedang"
    elif 35.5 <= c <= 55.4:
        i_low, i_high, c_low, c_high, category = 101, 150, 35.5, 55.4, "Tidak Sehat untuk Kelompok Sensitif"
    elif 55.5 <= c <= 150.4:
        i_low, i_high, c_low, c_high, category = 151, 200, 55.5, 150.4, "Tidak Sehat"
    elif 150.5 <= c <= 250.4:
        i_low, i_high, c_low, c_high, category = 201, 300, 150.5, 250.4, "Sangat Tidak Sehat"
    elif 250.5 <= c <= 500.4:
        i_low, i_high, c_low, c_high, category = 301, 500, 250.5, 500.4, "Berbahaya"
    else:
        return {
            "aqi": 501,
            "category": "Di Luar Indeks",
            "raw_pm25": pm25_concentration
        }

    aqi = round(((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low)

    return {
        "aqi": aqi,
        "category": category,
        "raw_pm25": pm25_concentration
    }

# Example
#location_id = 3038744
#print(air_quality(location_id))
#data_str = air_quality(location_id)
#print(data_str)
#print(extract_pm25_value(data_str))
#pm25 = extract_pm25_value(data_str)
#print(calculate_aqi_pm25(pm25))
