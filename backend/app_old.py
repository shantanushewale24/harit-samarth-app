"""
Soil Health Backend API Server
Serves ML predictions and sensor data analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from soil_health_ml import SoilHealthAnalyzer
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize analyzer
analyzer = SoilHealthAnalyzer()

# Load or train model on startup
def init_model():
    """Initialize the ML model"""
    model_dir = 'models'
    csv_path = 'data/data.csv'
    
    # Try to load existing model
    if analyzer.load_model(model_dir):
        logger.info("Loaded existing model")
        return
    
    # Train new model if doesn't exist
    if analyzer.train_on_csv(csv_path):
        analyzer.save_model(model_dir)
        logger.info("Trained and saved new model")
    else:
        logger.warning("Failed to initialize model")

# Initialize on startup
with app.app_context():
    init_model()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'soil-health-api'}), 200


@app.route('/api/soil-health/analyze', methods=['POST'])
def analyze_soil():
    """
    Analyze soil health from sensor reading
    
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
        
        # Prepare sensor reading
        sensor_reading = {field: float(data[field]) for field in required_fields}
        
        # Analyze
        analysis = analyzer.analyze_reading(sensor_reading)
        
        return jsonify(analysis), 200
    
    except ValueError as e:
        return jsonify({'error': f'Invalid data type: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error analyzing soil: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/soil-health/health-index', methods=['POST'])
def get_health_index():
    """
    Get soil biological health index (1-100)
    
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
        
        required_fields = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        sensor_reading = {field: float(data[field]) for field in required_fields}
        health_index, health_status = analyzer.calculate_soil_health_index(sensor_reading)
        
        return jsonify({
            'health_index': health_index,
            'health_status': health_status,
            'scale': '1-100'
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating health index: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/soil-health/anomaly', methods=['POST'])
def detect_anomaly():
    """
    Detect anomalies in sensor reading
    
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
        
        required_fields = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        sensor_reading = {field: float(data[field]) for field in required_fields}
        is_anomaly, anomaly_score = analyzer.detect_anomalies(sensor_reading)
        
        return jsonify({
            'is_anomalous': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'severity': 'High' if anomaly_score > 0.7 else 'Medium' if anomaly_score > 0.4 else 'Low'
        }), 200
    
    except Exception as e:
        logger.error(f"Error detecting anomaly: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/soil-health/critical-factors', methods=['POST'])
def get_critical_factors():
    """
    Get critical factors affecting soil health
    
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
        
        required_fields = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        sensor_reading = {field: float(data[field]) for field in required_fields}
        critical_factors = analyzer._identify_critical_factors(sensor_reading)
        
        return jsonify({
            'critical_factors': critical_factors,
            'factor_count': len(critical_factors),
            'status': 'Healthy' if len(critical_factors) == 0 else 'Needs Attention'
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting critical factors: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/soil-health/optimal-ranges', methods=['GET'])
def get_optimal_ranges():
    """
    Get optimal ranges for all parameters
    """
    optimal_ranges = {
        'N': {'min': 15, 'max': 30, 'unit': 'mg/kg', 'description': 'Nitrogen'},
        'P': {'min': 10, 'max': 25, 'unit': 'mg/kg', 'description': 'Phosphorus'},
        'K': {'min': 100, 'max': 200, 'unit': 'mg/kg', 'description': 'Potassium'},
        'CO2': {'min': 400, 'max': 600, 'unit': 'ppm', 'description': 'Carbon Dioxide'},
        'Temperature': {'min': 15, 'max': 25, 'unit': '°C', 'description': 'Temperature'},
        'Moisture': {'min': 40, 'max': 60, 'unit': '%', 'description': 'Moisture'},
        'pH': {'min': 6.5, 'max': 7.5, 'unit': 'pH', 'description': 'Acidity/Alkalinity'}
    }
    
    return jsonify({'optimal_ranges': optimal_ranges}), 200


@app.route('/api/soil-health/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple sensor readings in batch
    
    Request JSON:
    {
        "readings": [
            {"N": 22, "P": 18, "K": 150, "CO2": 500, "Temperature": 22, "Moisture": 55, "pH": 7.2},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if 'readings' not in data or not isinstance(data['readings'], list):
            return jsonify({'error': 'Invalid request format. Expected "readings" array'}), 400
        
        required_fields = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
        analyses = []
        
        for i, reading in enumerate(data['readings']):
            if not all(field in reading for field in required_fields):
                return jsonify({
                    'error': f'Missing fields in reading {i}',
                    'required': required_fields
                }), 400
            
            sensor_reading = {field: float(reading[field]) for field in required_fields}
            analysis = analyzer.analyze_reading(sensor_reading)
            analyses.append(analysis)
        
        return jsonify({
            'count': len(analyses),
            'analyses': analyses
        }), 200
    
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create necessary directories
    Path('models').mkdir(exist_ok=True)
    Path('data').mkdir(exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
