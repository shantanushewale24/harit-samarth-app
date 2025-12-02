"""
Production Configuration for Soil Health Backend
"""

import os
from pathlib import Path

# Base configuration
class Config:
    """Base configuration"""
    # Flask
    DEBUG = False
    TESTING = False
    
    # Server
    HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    PORT = int(os.getenv('SERVER_PORT', 5000))
    
    # ML Models
    MODEL_DIR = os.getenv('MODEL_DIR', 'models')
    DATA_DIR = os.getenv('DATA_DIR', 'data')
    CSV_PATH = os.getenv('CSV_PATH', 'data/data.csv')
    
    # ML Parameters
    ANOMALY_CONTAMINATION = float(os.getenv('ANOMALY_CONTAMINATION', 0.05))
    RF_ESTIMATORS = int(os.getenv('RF_ESTIMATORS', 100))
    RF_MAX_DEPTH = int(os.getenv('RF_MAX_DEPTH', 10))
    IF_ESTIMATORS = int(os.getenv('IF_ESTIMATORS', 100))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    CSV_PATH = 'data/test_data.csv'
    MODEL_DIR = 'models_test'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Restrict CORS in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://yourdomain.com').split(',')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])


# Optimal ranges configuration
OPTIMAL_RANGES = {
    'N': {
        'min': 15,
        'max': 30,
        'unit': 'mg/kg',
        'description': 'Nitrogen - Essential for plant growth',
        'critical_min': 10,
        'critical_max': 40
    },
    'P': {
        'min': 10,
        'max': 25,
        'unit': 'mg/kg',
        'description': 'Phosphorus - Important for root development',
        'critical_min': 5,
        'critical_max': 35
    },
    'K': {
        'min': 100,
        'max': 200,
        'unit': 'mg/kg',
        'description': 'Potassium - Vital for plant health',
        'critical_min': 50,
        'critical_max': 300
    },
    'CO2': {
        'min': 400,
        'max': 600,
        'unit': 'ppm',
        'description': 'Carbon Dioxide - Affects soil respiration',
        'critical_min': 300,
        'critical_max': 800
    },
    'Temperature': {
        'min': 15,
        'max': 25,
        'unit': '°C',
        'description': 'Soil Temperature - Affects microbial activity',
        'critical_min': 10,
        'critical_max': 30
    },
    'Moisture': {
        'min': 40,
        'max': 60,
        'unit': '%',
        'description': 'Soil Moisture - Critical for nutrient availability',
        'critical_min': 30,
        'critical_max': 70
    },
    'pH': {
        'min': 6.5,
        'max': 7.5,
        'unit': 'pH',
        'description': 'pH - Affects nutrient availability',
        'critical_min': 6.0,
        'critical_max': 8.0
    }
}

# Health index thresholds
HEALTH_STATUS_THRESHOLDS = {
    'Excellent': (75, 100),
    'Good': (60, 74),
    'Fair': (45, 59),
    'Poor': (30, 44),
    'Critical': (0, 29)
}

# Anomaly severity thresholds
ANOMALY_SEVERITY_THRESHOLDS = {
    'Low': (0.0, 0.33),
    'Medium': (0.34, 0.66),
    'High': (0.67, 1.0)
}

# Alert rules
ALERT_RULES = {
    'critical_health': {
        'threshold': 30,
        'severity': 'critical',
        'message': 'Soil health is critical. Immediate intervention required.'
    },
    'poor_health': {
        'threshold': 45,
        'severity': 'warning',
        'message': 'Soil health is poor. Review and adjust parameters.'
    },
    'anomaly_high': {
        'threshold': 0.7,
        'severity': 'warning',
        'message': 'High anomaly detected. Verify sensor calibration.'
    },
    'nitrogen_low': {
        'min': 10,
        'severity': 'info',
        'message': 'Nitrogen levels are low. Consider fertilization.'
    },
    'moisture_high': {
        'max': 70,
        'severity': 'warning',
        'message': 'Soil moisture is high. Risk of waterlogging.'
    }
}

# Caching configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'soil_health_'
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    'enabled': True,
    'requests_per_minute': 100,
    'requests_per_hour': 1000
}

# API versioning
API_VERSION = '1.0.0'
API_PREFIX = '/api'
