"""
Soil Health Backend with MySQL Database
Real-time sensor data processing with ML analysis
Saves data to both MySQL and CSV files
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import logging
import threading
import time
import json
import csv
import os
from typing import Optional
from dotenv import load_dotenv
import requests
import joblib
import pandas as pd

# Configure logging with better debug output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend_debug.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

# MySQL Database configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Update with your MySQL password if needed
    'database': 'soil_health_db',
    'port': 3306,
    'auth_plugin': 'mysql_native_password',
    'autocommit': True
}

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / 'data'
MODELS_DIR = BASE_DIR / 'models'

# CSV file path
CSV_PATH = str(DATA_DIR / 'sensor_readings.csv')
CROP_DATA_PATH = DATA_DIR / 'crop_recommendations.csv'
CROP_MODEL_PATH = MODELS_DIR / 'crop_recommender.pkl'
METRICS_PATH = MODELS_DIR / 'crop_recommender_metrics.json'

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '91c921b2103f4226b63110342250212')
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"

# Track MySQL availability
mysql_available = False

# Crop recommendation resources
crop_model = None
crop_dataset = None
crop_profiles = {}
crop_profiles_by_slug = {}

def get_mysql_connection():
    """Get MySQL connection with error handling"""
    global mysql_available
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        mysql_available = True
        return conn
    except Error as e:
        mysql_available = False
        logger.warning(f"MySQL Connection Warning: {e}")
        logger.warning("Falling back to CSV-only storage. Data will be saved to CSV only.")
        return None

def init_database():
    """Initialize MySQL database with schema (graceful fallback to CSV-only if MySQL unavailable)"""
    global mysql_available
    try:
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            port=MYSQL_CONFIG['port']
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        # Create sensor readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                N FLOAT,
                P FLOAT,
                K FLOAT,
                CO2 FLOAT,
                temperature FLOAT,
                moisture FLOAT,
                pH FLOAT,
                health_index INT,
                health_status VARCHAR(20),
                is_anomalous BOOLEAN,
                anomaly_score FLOAT,
                critical_factors JSON,
                INDEX idx_timestamp (timestamp)
            )
        ''')
        
        # Create analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sensor_id INT,
                analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                analysis_result JSON,
                FOREIGN KEY (sensor_id) REFERENCES sensor_readings(id),
                INDEX idx_sensor_id (sensor_id)
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        mysql_available = True
        logger.info("✅ MySQL Database initialized successfully")
        return True
    except Error as e:
        mysql_available = False
        logger.warning(f"⚠️  MySQL Connection Failed: {e}")
        logger.warning("⚠️  Falling back to CSV-only storage mode")
        logger.warning("💾 Data will be saved to: " + CSV_PATH)
        logger.info("To enable MySQL, update MYSQL_CONFIG credentials and restart")
        return False

def save_to_csv(sensor_data, health_index, health_status, is_anomalous, anomaly_score, critical_factors):
    """Save sensor reading to CSV file"""
    try:
        file_exists = os.path.exists(CSV_PATH)
        
        with open(CSV_PATH, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'N', 'P', 'K', 'CO2', 'Temperature', 
                         'Moisture', 'pH', 'health_index', 'health_status', 
                         'is_anomalous', 'anomaly_score', 'critical_factors']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if file doesn't exist
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'N': sensor_data.get('N'),
                'P': sensor_data.get('P'),
                'K': sensor_data.get('K'),
                'CO2': sensor_data.get('CO2'),
                'Temperature': sensor_data.get('Temperature'),
                'Moisture': sensor_data.get('Moisture'),
                'pH': sensor_data.get('pH'),
                'health_index': health_index,
                'health_status': health_status,
                'is_anomalous': is_anomalous,
                'anomaly_score': anomaly_score,
                'critical_factors': json.dumps(critical_factors)
            })
        
        logger.info(f"✓ Data saved to CSV: {CSV_PATH}")
    except Exception as e:
        logger.error(f"CSV save error: {e}")

def save_to_mysql(sensor_data, health_index, health_status, is_anomalous, anomaly_score, critical_factors):
    """Save sensor reading to MySQL database (graceful fallback if unavailable)"""
    try:
        conn = get_mysql_connection()
        if not conn:
            logger.debug("MySQL unavailable - data saved to CSV only")
            return None
        
        cursor = conn.cursor()
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        query = '''
            INSERT INTO sensor_readings 
            (N, P, K, CO2, temperature, moisture, pH, 
             health_index, health_status, is_anomalous, anomaly_score, critical_factors)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        values = (
            sensor_data.get('N'),
            sensor_data.get('P'),
            sensor_data.get('K'),
            sensor_data.get('CO2'),
            sensor_data.get('Temperature'),
            sensor_data.get('Moisture'),
            sensor_data.get('pH'),
            health_index,
            health_status,
            is_anomalous,
            anomaly_score,
            json.dumps(critical_factors)
        )
        
        cursor.execute(query, values)
        sensor_id = cursor.lastrowid
        conn.commit()
        
        logger.debug(f"✓ Data saved to MySQL (ID: {sensor_id})")
        
        cursor.close()
        conn.close()
        
        return sensor_id
    except Error as e:
        logger.warning(f"MySQL save failed: {e}. Data saved to CSV only.")
        return None

# Initialize database on startup
init_database()
load_crop_resources()

# ML Analysis functions (same as before)
def calculate_health_index(sensor_data):
    """Calculate soil health index (1-100) based on sensor readings"""
    score = 0
    weights = {
        'N': (15, 30, 1.0),      # optimal: 15-30
        'P': (10, 25, 1.0),      # optimal: 10-25
        'K': (100, 200, 1.0),    # optimal: 100-200
        'CO2': (400, 600, 0.8),  # optimal: 400-600
        'Temperature': (15, 25, 0.9),  # optimal: 15-25
        'Moisture': (40, 60, 1.0),     # optimal: 40-60
        'pH': (6.5, 7.5, 1.0)    # optimal: 6.5-7.5
    }
    
    total_weight = 0
    for param, (min_val, max_val, weight) in weights.items():
        value = sensor_data.get(param.lower() if param != 'CO2' else 'co2')
        if value is not None:
            # Calculate how close to optimal range
            if min_val <= value <= max_val:
                # Within optimal range
                distance_from_center = abs(value - (min_val + max_val) / 2)
                range_width = max_val - min_val
                param_score = (1 - distance_from_center / (range_width / 2)) * 100
            elif value < min_val:
                # Below optimal
                deficit = min_val - value
                param_score = max(0, 100 - deficit * 5)
            else:
                # Above optimal
                excess = value - max_val
                param_score = max(0, 100 - excess * 5)
            
            score += param_score * weight
            total_weight += weight
    
    health_index = int(score / total_weight) if total_weight > 0 else 50
    health_index = max(1, min(100, health_index))  # Clamp to 1-100
    
    # Determine status
    if health_index >= 75:
        status = "Excellent"
    elif health_index >= 60:
        status = "Good"
    elif health_index >= 45:
        status = "Fair"
    elif health_index >= 30:
        status = "Poor"
    else:
        status = "Critical"
    
    return health_index, status

def detect_anomalies(sensor_data):
    """Detect anomalies using statistical analysis"""
    # Define expected ranges
    ranges = {
        'nitrogen': (10, 40),
        'phosphorus': (5, 35),
        'potassium': (50, 300),
        'co2': (300, 800),
        'temperature': (10, 30),
        'moisture': (30, 70),
        'ph': (5.0, 8.0)
    }
    
    is_anomalous = False
    anomaly_score = 0.0
    anomalies_count = 0
    
    for param, (min_val, max_val) in ranges.items():
        value = sensor_data.get(param)
        if value is not None:
            if value < min_val or value > max_val:
                is_anomalous = True
                anomalies_count += 1
                # Calculate anomaly severity
                if value < min_val:
                    deviation = (min_val - value) / min_val
                else:
                    deviation = (value - max_val) / max_val
                anomaly_score = max(anomaly_score, min(1.0, abs(deviation)))
    
    # Average anomaly score
    if anomalies_count > 0:
        anomaly_score = anomaly_score / len(ranges)
    
    return is_anomalous, anomaly_score

def identify_critical_factors(sensor_data):
    """Identify critical factors affecting soil health"""
    critical_factors = []
    
    params = {
        'N': (15, 30, 'Nitrogen'),
        'P': (10, 25, 'Phosphorus'),
        'K': (100, 200, 'Potassium'),
        'CO2': (400, 600, 'CO2'),
        'Temperature': (15, 25, 'Temperature'),
        'Moisture': (40, 60, 'Moisture'),
        'pH': (6.5, 7.5, 'pH')
    }
    
    for key, (min_val, max_val, name) in params.items():
        param_key = key.lower() if key != 'CO2' else 'co2'
        value = sensor_data.get(param_key)
        if value is not None:
            if value < min_val or value > max_val:
                critical_factors.append(name)
    
    return critical_factors


# ---------------------------------------------------------------------------
# Crop recommendation utilities (Weather + ML pipeline)
# ---------------------------------------------------------------------------

CROP_ENRICHMENT = {
    "Rice": {
        "vernacular": "धान",
        "summary": "Thrives in standing water and humid monsoon belts.",
        "expected_yield": "4-5 tons/hectare",
        "duration": "120-150 days",
        "management": [
            "Maintain 5-7 cm of standing water during vegetative stage",
            "Split nitrogen into three dressings to avoid lodging",
            "Plan harvest when grains reach 20-22% moisture"
        ]
    },
    "Wheat": {
        "vernacular": "गेहूं",
        "summary": "Prefers cool winters with well-drained loamy soils.",
        "expected_yield": "3-4 tons/hectare",
        "duration": "110-130 days",
        "management": [
            "Keep sowing depth 4-5 cm for uniform germination",
            "Irrigate at crown-root initiation and flowering",
            "Ensure timely rust surveillance in humid belts"
        ]
    },
    "Soybean": {
        "vernacular": "सोयाबीन",
        "summary": "Nitrogen-fixing legume suited to warm semi-arid belts.",
        "expected_yield": "2-3 tons/hectare",
        "duration": "90-120 days",
        "management": [
            "Use well-inoculated seed to boost nodulation",
            "Avoid waterlogging during pod fill",
            "Harvest when 80% pods turn brown"
        ]
    },
    "Groundnut": {
        "vernacular": "मूंगफली",
        "summary": "Requires friable sandy loam with assured pod development.",
        "expected_yield": "2.5-3 tons/hectare",
        "duration": "110-130 days",
        "management": [
            "Gypsum application at flowering improves pegging",
            "Light irrigation after pegging avoids shrivelled kernels",
            "Windrow plants for 2-3 days before threshing"
        ]
    },
    "Cotton": {
        "vernacular": "कपास",
        "summary": "Deep-rooted crop for black soils with long frost-free period.",
        "expected_yield": "1.8-2.2 tons lint/hectare",
        "duration": "150-180 days",
        "management": [
            "Adopt square-retention sprays in high bollworm pressure",
            "Maintain 70-80 cm row spacing for aeration",
            "Schedule defoliant 10 days before picking"
        ]
    },
    "Chickpea": {
        "vernacular": "चना",
        "summary": "Cool-season pulse suited to residual soil moisture.",
        "expected_yield": "1.5-2 tons/hectare",
        "duration": "100-120 days",
        "management": [
            "Seed treatment with Rhizobium for nodulation",
            "Avoid heavy irrigation during flowering",
            "Harvest when pods turn straw yellow"
        ]
    },
    "Bajra": {
        "vernacular": "बाजरा",
        "summary": "Hardy millet for arid zones with erratic rainfall.",
        "expected_yield": "2-2.5 tons/hectare",
        "duration": "75-95 days",
        "management": [
            "Use short-duration hybrids for late sowing",
            "Thin seedlings at 15 DAS for optimal tillers",
            "Apply life-saving irrigation at booting"
        ]
    },
    "Sugarcane": {
        "vernacular": "गन्ना",
        "summary": "Long-duration cash crop needing abundant water and nutrients.",
        "expected_yield": "80-100 tons/hectare",
        "duration": "270-330 days",
        "management": [
            "Trash mulching conserves moisture and controls weeds",
            "Adopt drip + fertigation for higher recovery",
            "Detrash at 150 days to reduce pest niches"
        ]
    }
}


def slugify_crop(name: str) -> str:
    return name.lower().replace(' ', '-').replace('/', '-').replace('&', 'and')


def build_crop_profiles(df: pd.DataFrame):
    profiles = {}
    if df is None or df.empty:
        return profiles

    grouped = df.groupby('recommended_crop').first().reset_index()
    for _, row in grouped.iterrows():
        crop_name = row['recommended_crop']
        slug = slugify_crop(crop_name)
        enrichment = CROP_ENRICHMENT.get(crop_name, {})
        profile = {
            'crop': crop_name,
            'slug': slug,
            'season': row.get('primary_season'),
            'climate_zone': row.get('climate_zone'),
            'soil_type': row.get('soil_type'),
            'irrigation': row.get('irrigation'),
            'risks': {
                'wind': row.get('wind_risk'),
                'drought': row.get('drought_risk'),
                'flood': row.get('flood_risk'),
            },
            'ph_range': [row.get('ph_min'), row.get('ph_max')],
            'altitude_m': row.get('altitude_m'),
            'monsoon_intensity': row.get('monsoon_intensity'),
            'summary': enrichment.get('summary', f"Suitable for {row.get('climate_zone')} conditions."),
            'vernacular': enrichment.get('vernacular'),
            'expected_yield': enrichment.get('expected_yield'),
            'duration': enrichment.get('duration'),
            'management': enrichment.get('management', []),
        }
        profiles[crop_name] = profile
    return profiles


def load_crop_resources():
    global crop_model, crop_dataset, crop_profiles, crop_profiles_by_slug
    try:
        if CROP_MODEL_PATH.exists():
            crop_model = joblib.load(CROP_MODEL_PATH)
            logger.info("✅ Crop recommendation model loaded")
        else:
            logger.warning("Crop model file not found at %s", CROP_MODEL_PATH)
            crop_model = None
    except Exception as exc:
        logger.warning("Unable to load crop model: %s", exc)
        crop_model = None

    try:
        if CROP_DATA_PATH.exists():
            crop_dataset = pd.read_csv(CROP_DATA_PATH)
            logger.info("📈 Crop dataset loaded (%d rows)", len(crop_dataset))
        else:
            logger.warning("Crop dataset not found at %s", CROP_DATA_PATH)
            crop_dataset = None
    except Exception as exc:
        logger.warning("Unable to load crop dataset: %s", exc)
        crop_dataset = None

    if crop_dataset is not None:
        crop_profiles = build_crop_profiles(crop_dataset)
        crop_profiles_by_slug = {profile['slug']: profile for profile in crop_profiles.values()}
    else:
        crop_profiles = {}
        crop_profiles_by_slug = {}


def get_weather_for_location(location: str) -> dict:
    if not WEATHER_API_KEY:
        raise ValueError("Weather API key missing. Set WEATHER_API_KEY env variable.")
    params = {
        'key': WEATHER_API_KEY,
        'q': location,
        'aqi': 'no'
    }
    response = requests.get(WEATHER_API_URL, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    current = payload.get('current', {})
    weather = {
        'location': f"{payload['location']['name']}, {payload['location']['region']}",
        'raw_location': payload['location'],
        'condition': current.get('condition', {}).get('text'),
        'description': f"Feels like {current.get('feelslike_c')}°C",
        'temperature': current.get('temp_c'),
        'humidity': current.get('humidity'),
        'windSpeed': round((current.get('wind_kph', 0) or 0) * 0.277778, 2),
        'rainfall': current.get('precip_mm', 0) or 0,
        'visibility': current.get('vis_km'),
        'last_updated': current.get('last_updated')
    }
    return weather


def select_region_profile(user_location: str, weather: Optional[dict]):
    if crop_dataset is None or crop_dataset.empty:
        raise ValueError("Crop dataset unavailable")

    search_terms = [user_location]
    if weather and weather.get('raw_location'):
        search_terms.extend([
            weather['raw_location'].get('region'),
            weather['raw_location'].get('name'),
            weather['raw_location'].get('tz_id')
        ])

    for term in filter(None, search_terms):
        mask = crop_dataset['state'].str.contains(term, case=False, na=False)
        if mask.any():
            return crop_dataset[mask].iloc[0]
        mask = crop_dataset['region'].str.contains(term, case=False, na=False)
        if mask.any():
            return crop_dataset[mask].iloc[0]

    return crop_dataset.sample(1, random_state=42).iloc[0]


def prepare_feature_vector(row: pd.Series, weather: Optional[dict]):
    feature = row.drop(labels=['recommended_crop']).to_dict()

    if weather:
        temp = weather.get('temperature')
        if temp is not None:
            feature['temp_min_c'] = temp - 2
            feature['temp_max_c'] = temp + 2
        humidity = weather.get('humidity')
        if humidity is not None:
            feature['humidity_min_pct'] = max(0, humidity - 10)
            feature['humidity_max_pct'] = min(100, humidity + 10)
        rainfall = weather.get('rainfall')
        if rainfall is not None:
            feature['rainfall_min_mm'] = max(0, rainfall * 0.8)
            feature['rainfall_max_mm'] = rainfall * 1.2 + 1

    return feature


def score_crops(feature: dict):
    if crop_model is None:
        raise ValueError("Crop model not loaded")

    feature_df = pd.DataFrame([feature])
    rankings = []

    if hasattr(crop_model, 'predict_proba'):
        probabilities = crop_model.predict_proba(feature_df)[0]
        classes = crop_model.classes_
        rankings = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
    else:
        prediction = crop_model.predict(feature_df)
        rankings = [(prediction[0], 1.0)]

    recommendations = []
    for crop_name, probability in rankings[:3]:
        profile = crop_profiles.get(crop_name, {'slug': slugify_crop(crop_name)})
        recommendations.append({
            'crop': crop_name,
            'slug': profile.get('slug', slugify_crop(crop_name)),
            'vernacular': profile.get('vernacular'),
            'season': profile.get('season'),
            'summary': profile.get('summary'),
            'expected_yield': profile.get('expected_yield'),
            'duration': profile.get('duration'),
            'soil_type': profile.get('soil_type'),
            'climate_zone': profile.get('climate_zone'),
            'irrigation': profile.get('irrigation'),
            'risks': profile.get('risks'),
            'management': profile.get('management', []),
            'suitability': int(round(float(probability) * 100))
        })

    return recommendations

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'soil-health-api'}), 200


@app.route('/api/crops/recommendations', methods=['POST'])
def crop_recommendations():
    if crop_model is None or crop_dataset is None:
        return jsonify({'error': 'Crop recommendation model is unavailable. Train the model and restart the backend.'}), 503

    payload = request.get_json() or {}
    location = payload.get('location') or payload.get('city')
    if not location:
        return jsonify({'error': 'Location is required to fetch localized weather data.'}), 400

    try:
        weather = get_weather_for_location(location)
        profile_row = select_region_profile(location, weather)
        feature_vector = prepare_feature_vector(profile_row, weather)
        recommendations = score_crops(feature_vector)

        response = {
            'weather': {
                'location': weather.get('location'),
                'condition': weather.get('condition'),
                'description': weather.get('description'),
                'temperature': weather.get('temperature'),
                'humidity': weather.get('humidity'),
                'windSpeed': weather.get('windSpeed'),
                'rainfall': weather.get('rainfall'),
                'last_updated': weather.get('last_updated')
            },
            'recommendations': recommendations,
            'source_region': {
                'region': profile_row.get('region'),
                'state': profile_row.get('state'),
                'climate_zone': profile_row.get('climate_zone'),
                'primary_season': profile_row.get('primary_season'),
                'monsoon_intensity': profile_row.get('monsoon_intensity')
            },
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }
        return jsonify(response), 200
    except requests.HTTPError as http_err:
        logger.error("Weather API failure: %s", http_err)
        return jsonify({'error': 'Unable to fetch weather data', 'details': str(http_err)}), 502
    except Exception as exc:
        logger.exception("Crop recommendation pipeline failed")
        return jsonify({'error': 'Failed to generate crop recommendations', 'details': str(exc)}), 500


@app.route('/api/crops/details/<slug>', methods=['GET'])
def crop_details(slug: str):
    if not crop_profiles_by_slug:
        return jsonify({'error': 'Crop knowledge base unavailable'}), 503

    profile = crop_profiles_by_slug.get(slug)
    if not profile:
        # Attempt lookup by crop name
        matching = next((p for p in crop_profiles.values() if slugify_crop(p['crop']) == slug), None)
        if not matching:
            return jsonify({'error': 'Crop not found'}), 404
        profile = matching

    return jsonify(profile), 200

@app.route('/api/soil-health/analyze', methods=['POST'])
def analyze_soil():
    """
    Analyze soil health from sensor reading and store in database
    
    Request JSON:
    {
        "N": 22,
        "P": 18,
        "K": 150,
        "CO2": 500,
        "Temperature": 22,
        "Moisture": 55,
        "pH": 7.2
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # Convert to normalized keys for analysis
        sensor_data = {
            'nitrogen': float(data['N']),
            'phosphorus': float(data['P']),
            'potassium': float(data['K']),
            'co2': float(data['CO2']),
            'temperature': float(data['Temperature']),
            'moisture': float(data['Moisture']),
            'ph': float(data['pH'])
        }
        
        # Perform analysis
        health_index, health_status = calculate_health_index(sensor_data)
        is_anomalous, anomaly_score = detect_anomalies(sensor_data)
        critical_factors = identify_critical_factors(sensor_data)
        
        # Store to both CSV and MySQL
        save_to_csv(
            {'N': data['N'], 'P': data['P'], 'K': data['K'], 'CO2': data['CO2'], 
             'Temperature': data['Temperature'], 'Moisture': data['Moisture'], 'pH': data['pH']},
            health_index, health_status, is_anomalous, anomaly_score, critical_factors
        )
        
        # Also save to MySQL
        try:
            sensor_id = save_to_mysql(
                {'N': data['N'], 'P': data['P'], 'K': data['K'], 'CO2': data['CO2'],
                 'Temperature': data['Temperature'], 'Moisture': data['Moisture'], 'pH': data['pH']},
                health_index, health_status, is_anomalous, anomaly_score, critical_factors
            )
        except Exception as mysql_error:
            logger.error(f"MySQL save failed: {str(mysql_error)}. CSV saved successfully.")
        
        # Return analysis
        response = {
            'timestamp': datetime.now().isoformat(),
            'soil_health_index': health_index,
            'health_status': health_status,
            'is_anomalous': is_anomalous,
            'anomaly_score': float(anomaly_score),
            'critical_factors': critical_factors,
            'sensor_readings': {
                'N': data['N'],
                'P': data['P'],
                'K': data['K'],
                'CO2': data['CO2'],
                'Temperature': data['Temperature'],
                'Moisture': data['Moisture'],
                'pH': data['pH']
            }
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({'error': f'Invalid data type: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error analyzing soil: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/soil-health/latest', methods=['GET'])
def get_latest_reading():
    """Get the latest sensor reading and analysis from MySQL (or CSV if MySQL unavailable)"""
    try:
        conn = get_mysql_connection()
        
        # If MySQL is available, use it
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT timestamp, N, P, K, CO2, temperature, 
                       moisture, pH, health_index, health_status, is_anomalous, 
                       anomaly_score, critical_factors
                FROM sensor_readings
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not result:
                return jsonify({'error': 'No readings available', 'mode': 'MySQL'}), 404
            
            critical_factors = []
            if result.get('critical_factors'):
                try:
                    critical_factors = json.loads(result['critical_factors'])
                except:
                    critical_factors = []
            
            return jsonify({
                'timestamp': result['timestamp'].isoformat() if result['timestamp'] else None,
                'soil_health_index': result['health_index'],
                'health_status': result['health_status'],
                'is_anomalous': result['is_anomalous'],
                'anomaly_score': float(result['anomaly_score']),
                'critical_factors': critical_factors,
                'sensor_readings': {
                    'N': float(result['N']),
                    'P': float(result['P']),
                    'K': float(result['K']),
                    'CO2': float(result['CO2']),
                    'Temperature': float(result['temperature']),
                    'Moisture': float(result['moisture']),
                    'pH': float(result['pH'])
                },
                'mode': 'MySQL'
            }), 200
        else:
            # Fallback to CSV if MySQL is unavailable
            if os.path.exists(CSV_PATH):
                with open(CSV_PATH, 'r') as f:
                    reader = list(csv.DictReader(f))
                    if reader:
                        latest = reader[-1]  # Get last row
                        return jsonify({
                            'timestamp': latest.get('timestamp'),
                            'soil_health_index': int(latest.get('health_index', 0)),
                            'health_status': latest.get('health_status'),
                            'is_anomalous': latest.get('is_anomalous') == 'True',
                            'anomaly_score': float(latest.get('anomaly_score', 0)),
                            'critical_factors': json.loads(latest.get('critical_factors', '[]')),
                            'sensor_readings': {
                                'N': float(latest.get('N', 0)),
                                'P': float(latest.get('P', 0)),
                                'K': float(latest.get('K', 0)),
                                'CO2': float(latest.get('CO2', 0)),
                                'Temperature': float(latest.get('Temperature', 0)),
                                'Moisture': float(latest.get('Moisture', 0)),
                                'pH': float(latest.get('pH', 0))
                            },
                            'mode': 'CSV-Fallback',
                            'warning': 'MySQL unavailable, serving from CSV backup'
                        }), 200
            
            return jsonify({'error': 'No data available', 'mode': 'CSV-Fallback'}), 404
    
    except Exception as e:
        logger.error(f"Error fetching latest reading: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/soil-health/history', methods=['GET'])
def get_history():
    """Get sensor reading history from MySQL (or CSV fallback, default last 100 readings)"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        conn = get_mysql_connection()
        
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT timestamp, N, P, K, CO2, temperature,
                       moisture, pH, health_index, health_status, is_anomalous,
                       anomaly_score
                FROM sensor_readings
                ORDER BY timestamp DESC
                LIMIT %s
            ''', (limit,))
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            readings = []
            for row in results:
                readings.append({
                    'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None,
                    'health_index': row['health_index'],
                    'health_status': row['health_status'],
                    'is_anomalous': row['is_anomalous'],
                    'anomaly_score': float(row['anomaly_score']),
                    'sensor_readings': {
                        'N': float(row['N']),
                        'P': float(row['P']),
                        'K': float(row['K']),
                        'CO2': float(row['CO2']),
                        'Temperature': float(row['temperature']),
                        'Moisture': float(row['moisture']),
                        'pH': float(row['pH'])
                    }
                })
            
            return jsonify({
                'total': len(readings),
                'readings': readings,
                'mode': 'MySQL'
            }), 200
        else:
            # Fallback to CSV
            if os.path.exists(CSV_PATH):
                with open(CSV_PATH, 'r') as f:
                    reader = list(csv.DictReader(f))
                    # Get last 'limit' rows
                    rows = reader[-limit:] if reader else []
                    
                    readings = []
                    for row in reversed(rows):  # Reverse to show newest first
                        try:
                            readings.append({
                                'timestamp': row.get('timestamp'),
                                'health_index': int(row.get('health_index', 0)),
                                'health_status': row.get('health_status'),
                                'is_anomalous': row.get('is_anomalous') == 'True',
                                'anomaly_score': float(row.get('anomaly_score', 0)),
                                'sensor_readings': {
                                    'N': float(row.get('N', 0)),
                                    'P': float(row.get('P', 0)),
                                    'K': float(row.get('K', 0)),
                                    'CO2': float(row.get('CO2', 0)),
                                    'Temperature': float(row.get('Temperature', 0)),
                                    'Moisture': float(row.get('Moisture', 0)),
                                    'pH': float(row.get('pH', 0))
                                }
                            })
                        except Exception as row_error:
                            logger.warning(f"Error parsing CSV row: {row_error}")
                            continue
                    
                    return jsonify({
                        'total': len(readings),
                        'readings': readings,
                        'mode': 'CSV-Fallback',
                        'warning': 'MySQL unavailable, serving from CSV backup'
                    }), 200
            
            return jsonify({'error': 'No data available', 'mode': 'CSV-Fallback'}), 404
    
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/soil-health/stats', methods=['GET'])
def get_stats():
    """Get statistics about sensor readings from MySQL (or CSV fallback)"""
    try:
        conn = get_mysql_connection()
        
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get total readings
            cursor.execute('SELECT COUNT(*) as count FROM sensor_readings')
            total_readings = cursor.fetchone()['count']
            
            # Get average health index
            cursor.execute('SELECT AVG(health_index) as avg_health FROM sensor_readings')
            avg_health_row = cursor.fetchone()
            avg_health = avg_health_row['avg_health'] or 0 if avg_health_row else 0
            
            # Get anomaly count
            cursor.execute('SELECT COUNT(*) as count FROM sensor_readings WHERE is_anomalous = 1')
            anomaly_count = cursor.fetchone()['count']
            
            # Get health status distribution
            cursor.execute('''
                SELECT health_status, COUNT(*) as count
                FROM sensor_readings
                GROUP BY health_status
            ''')
            status_dist = {row['health_status']: row['count'] for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'total_readings': total_readings,
                'average_health_index': round(float(avg_health), 2),
                'anomaly_count': anomaly_count,
                'anomaly_percentage': round((anomaly_count / total_readings * 100) if total_readings > 0 else 0, 2),
                'status_distribution': status_dist,
                'mode': 'MySQL'
            }), 200
        else:
            # Fallback to CSV
            if os.path.exists(CSV_PATH):
                with open(CSV_PATH, 'r') as f:
                    reader = list(csv.DictReader(f))
                    
                    if not reader:
                        return jsonify({
                            'total_readings': 0,
                            'average_health_index': 0,
                            'anomaly_count': 0,
                            'anomaly_percentage': 0,
                            'status_distribution': {},
                            'mode': 'CSV-Fallback'
                        }), 200
                    
                    # Calculate statistics from CSV
                    total_readings = len(reader)
                    health_indices = []
                    anomaly_count = 0
                    status_dist = {}
                    
                    for row in reader:
                        try:
                            health_idx = int(row.get('health_index', 0))
                            health_indices.append(health_idx)
                            
                            if row.get('is_anomalous') == 'True':
                                anomaly_count += 1
                            
                            status = row.get('health_status', 'Unknown')
                            status_dist[status] = status_dist.get(status, 0) + 1
                        except Exception as row_error:
                            logger.warning(f"Error parsing CSV row: {row_error}")
                            continue
                    
                    avg_health = sum(health_indices) / len(health_indices) if health_indices else 0
                    
                    return jsonify({
                        'total_readings': total_readings,
                        'average_health_index': round(avg_health, 2),
                        'anomaly_count': anomaly_count,
                        'anomaly_percentage': round((anomaly_count / total_readings * 100) if total_readings > 0 else 0, 2),
                        'status_distribution': status_dist,
                        'mode': 'CSV-Fallback',
                        'warning': 'MySQL unavailable, serving from CSV backup'
                    }), 200
            
            return jsonify({
                'total_readings': 0,
                'average_health_index': 0,
                'anomaly_count': 0,
                'anomaly_percentage': 0,
                'status_distribution': {},
                'mode': 'CSV-Fallback',
                'error': 'No data available'
            }), 200
    
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

def check_mysql_status():
    """Check MySQL server status and connectivity"""
    logger.info("=" * 60)
    logger.info("🔍 MySQL Diagnostics")
    logger.info("=" * 60)
    
    logger.info(f"MySQL Host: {MYSQL_CONFIG['host']}")
    logger.info(f"MySQL Port: {MYSQL_CONFIG['port']}")
    logger.info(f"MySQL User: {MYSQL_CONFIG['user']}")
    logger.info(f"MySQL Database: {MYSQL_CONFIG['database']}")
    
    try:
        # Try to connect without specifying database first
        test_conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            port=MYSQL_CONFIG['port']
        )
        server_info = test_conn.get_server_info()
        logger.info(f"✅ MySQL Server Connected - Version: {server_info}")
        test_conn.close()
        return True
    except Error as e:
        error_code = str(e).split('(')[1].split(')')[0] if '(' in str(e) else 'Unknown'
        logger.error("=" * 60)
        logger.error(f"❌ MySQL Connection Failed!")
        logger.error("=" * 60)
        logger.error(f"Error Code: {error_code}")
        logger.error(f"Error Message: {e}")
        logger.error("")
        logger.error("🔧 Troubleshooting Guide:")
        logger.error("")
        
        if '1045' in str(e) or 'Access denied' in str(e):
            logger.error("❌ ERROR 1045: Access Denied")
            logger.error("   Issue: Wrong password or user doesn't exist")
            logger.error(f"   Action: Update MYSQL_CONFIG['password']")
            logger.error(f"   Or test: mysql -u {MYSQL_CONFIG['user']} -h {MYSQL_CONFIG['host']} -p")
        elif '2003' in str(e) or 'Connection refused' in str(e):
            logger.error("❌ ERROR 2003: Connection Refused")
            logger.error("   Issue: MySQL server is NOT running")
            logger.error("   Action: Start MySQL server:")
            logger.error("      Windows: net start MySQL80 (or your service name)")
            logger.error("      Mac:     brew services start mysql")
            logger.error("      Linux:   sudo systemctl start mysql")
        elif '2002' in str(e) or 'Can\'t connect' in str(e):
            logger.error("❌ ERROR 2002: Can't Connect to Socket")
            logger.error("   Issue: MySQL socket issue or server not running")
            logger.error("   Action: Check if MySQL service is running")
        else:
            logger.error("   Unknown error: {e}")
        
        logger.error("")
        logger.error("💾 Falling back to CSV-only mode")
        logger.error("=" * 60)
        return False

def start_sensor_generator():
    """Start sensor data generator in a background thread"""
    try:
        from sensor_generator import SensorDataGenerator
        
        generator = SensorDataGenerator()
        generator.running = True
        thread = generator.start()
        logger.info("✅ Sensor data generator started in background")
        return thread
    except Exception as e:
        logger.warning(f"⚠️  Could not start sensor generator: {e}")
        logger.info("   Continue without sensor generator - you can send data via API")
        return None

if __name__ == '__main__':
    logger.info("\n" + "=" * 60)
    logger.info("🚀 Harit Samarth Backend - Starting Up")
    logger.info("=" * 60)
    
    # Check MySQL status
    check_mysql_status()
    
    # Initialize database (will use CSV if MySQL fails)
    logger.info("\nInitializing database...")
    init_database()
    logger.info("✅ Database initialization complete")
    
    # Start sensor data generator
    logger.info("\nStarting sensor data generator...")
    start_sensor_generator()
    
    # Show how to debug
    logger.info("\n" + "=" * 60)
    logger.info("📊 Debugging & Monitoring")
    logger.info("=" * 60)
    logger.info("To check database tables:")
    logger.info("  python debug_mysql.py")
    logger.info("\nTo test the API:")
    logger.info("  curl http://localhost:5000/api/soil-health/stats")
    logger.info("  curl http://localhost:5000/api/soil-health/latest")
    logger.info("\nLogs are saved to: backend_debug.log")
    logger.info("=" * 60 + "\n")
    
    # Run Flask app
    logger.info("🌐 Starting Flask server on http://0.0.0.0:5000")
    logger.info("   Frontend: http://localhost:8080")
    app.run(host='0.0.0.0', port=5000, debug=True)
