"""
Soil Health Dashboard - ML Backend
Uses Random Forest for anomaly detection and soil biological health scoring
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
import json
from datetime import datetime

class SoilHealthAnalyzer:
    """
    Analyzes soil health based on sensor readings and calculates:
    1. Anomaly detection using Random Forest
    2. Biological health index (1-100 scale)
    """
    
    def __init__(self):
        self.rf_model = None
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.feature_columns = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
        self.health_index_model = None
        
    def generate_synthetic_training_data(self, csv_path='data/data.csv'):
        """
        Load CSV data and prepare it for model training
        """
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} records from {csv_path}")
            return df
        except FileNotFoundError:
            print(f"CSV file not found at {csv_path}")
            return None
    
    def prepare_features(self, df):
        """
        Extract and normalize features from dataframe
        """
        X = df[self.feature_columns].values
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, X
    
    def train_anomaly_detector(self, X_scaled):
        """
        Train Isolation Forest for anomaly detection
        """
        self.isolation_forest = IsolationForest(
            contamination=0.05,  # 5% anomalies
            random_state=42,
            n_estimators=100
        )
        anomalies = self.isolation_forest.fit_predict(X_scaled)
        return anomalies
    
    def train_health_index_model(self, df):
        """
        Train Random Forest to predict soil health index
        Uses actual sensor readings to establish baseline
        """
        # Create synthetic labels based on sensor characteristics
        # Healthy soil characteristics:
        # N, P, K: moderate levels (15-30 mg/kg)
        # CO2: moderate (400-600 ppm)
        # Temperature: optimal (15-25°C)
        # Moisture: optimal (40-60%)
        # pH: near neutral (6.5-7.5)
        
        X = df[self.feature_columns].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Create labels: 1 for healthy, 0 for poor
        health_labels = np.zeros(len(df))
        for i in range(len(df)):
            score = self._calculate_health_label(df.iloc[i])
            health_labels[i] = 1 if score > 0.6 else 0
        
        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.rf_model.fit(X_scaled, health_labels)
        print("Health index model trained")
        
        return self.rf_model
    
    def _calculate_health_label(self, row):
        """
        Calculate health label (0-1) based on sensor readings
        """
        score = 0
        
        # N: 15-30 is optimal
        if 15 <= row['N'] <= 30:
            score += 0.15
        elif 10 <= row['N'] <= 40:
            score += 0.08
        
        # P: 10-25 is optimal
        if 10 <= row['P'] <= 25:
            score += 0.15
        elif 5 <= row['P'] <= 35:
            score += 0.08
        
        # K: 100-200 is optimal
        if 100 <= row['K'] <= 200:
            score += 0.15
        elif 50 <= row['K'] <= 300:
            score += 0.08
        
        # CO2: 400-600 ppm is good
        if 400 <= row['CO2'] <= 600:
            score += 0.15
        elif 300 <= row['CO2'] <= 800:
            score += 0.08
        
        # Temperature: 15-25°C is optimal
        if 15 <= row['Temperature'] <= 25:
            score += 0.15
        elif 10 <= row['Temperature'] <= 30:
            score += 0.08
        
        # Moisture: 40-60% is optimal
        if 40 <= row['Moisture'] <= 60:
            score += 0.15
        elif 30 <= row['Moisture'] <= 70:
            score += 0.08
        
        # pH: 6.5-7.5 is optimal
        if 6.5 <= row['pH'] <= 7.5:
            score += 0.15
        elif 6.0 <= row['pH'] <= 8.0:
            score += 0.08
        
        return score
    
    def calculate_soil_health_index(self, sensor_reading, normalized=True):
        """
        Calculate soil biological health index (1-100) based on sensor reading
        
        Args:
            sensor_reading: dict with keys ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
            normalized: whether to normalize the reading
        
        Returns:
            health_index (1-100), health_status (string)
        """
        if normalized:
            reading_array = np.array([[sensor_reading[col] for col in self.feature_columns]])
            reading_scaled = self.scaler.transform(reading_array)
        else:
            reading_scaled = np.array([[sensor_reading[col] for col in self.feature_columns]])
        
        # Get probability from Random Forest
        if self.rf_model:
            health_prob = self.rf_model.predict_proba(reading_scaled)[0][1]
        else:
            health_prob = 0.5
        
        # Convert to 1-100 scale
        health_index = int(health_prob * 100)
        
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
    
    def detect_anomalies(self, sensor_reading, normalized=True):
        """
        Detect if sensor reading is anomalous
        
        Returns:
            is_anomaly (bool), anomaly_score (float)
        """
        if not self.isolation_forest:
            return False, 0.0
        
        if normalized:
            reading_array = np.array([[sensor_reading[col] for col in self.feature_columns]])
            reading_scaled = self.scaler.transform(reading_array)
        else:
            reading_scaled = np.array([[sensor_reading[col] for col in self.feature_columns]])
        
        anomaly_pred = self.isolation_forest.predict(reading_scaled)[0]
        anomaly_score = -self.isolation_forest.score_samples(reading_scaled)[0]
        
        is_anomaly = anomaly_pred == -1
        
        return is_anomaly, anomaly_score
    
    def analyze_reading(self, sensor_reading, normalized=True):
        """
        Complete analysis of a sensor reading
        
        Returns:
            dict with health index, status, anomaly detection, and analysis
        """
        health_index, health_status = self.calculate_soil_health_index(sensor_reading, normalized)
        is_anomaly, anomaly_score = self.detect_anomalies(sensor_reading, normalized)
        
        # Determine critical factors
        critical_factors = self._identify_critical_factors(sensor_reading)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'soil_health_index': health_index,
            'health_status': health_status,
            'is_anomalous': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'critical_factors': critical_factors,
            'sensor_reading': sensor_reading
        }
        
        return analysis
    
    def _identify_critical_factors(self, sensor_reading):
        """
        Identify which factors are affecting soil health negatively
        """
        critical_factors = []
        
        if sensor_reading['N'] < 10 or sensor_reading['N'] > 40:
            critical_factors.append(f"Nitrogen: {sensor_reading['N']} (Optimal: 15-30)")
        
        if sensor_reading['P'] < 5 or sensor_reading['P'] > 35:
            critical_factors.append(f"Phosphorus: {sensor_reading['P']} (Optimal: 10-25)")
        
        if sensor_reading['K'] < 50 or sensor_reading['K'] > 300:
            critical_factors.append(f"Potassium: {sensor_reading['K']} (Optimal: 100-200)")
        
        if sensor_reading['CO2'] < 300 or sensor_reading['CO2'] > 800:
            critical_factors.append(f"CO2: {sensor_reading['CO2']} (Optimal: 400-600)")
        
        if sensor_reading['Temperature'] < 10 or sensor_reading['Temperature'] > 30:
            critical_factors.append(f"Temperature: {sensor_reading['Temperature']}°C (Optimal: 15-25°C)")
        
        if sensor_reading['Moisture'] < 30 or sensor_reading['Moisture'] > 70:
            critical_factors.append(f"Moisture: {sensor_reading['Moisture']}% (Optimal: 40-60%)")
        
        if sensor_reading['pH'] < 6.0 or sensor_reading['pH'] > 8.0:
            critical_factors.append(f"pH: {sensor_reading['pH']} (Optimal: 6.5-7.5)")
        
        return critical_factors
    
    def train_on_csv(self, csv_path):
        """
        Train the model on CSV data
        """
        df = self.generate_synthetic_training_data(csv_path)
        if df is None:
            return False
        
        X_scaled, X = self.prepare_features(df)
        
        # Train anomaly detector
        self.train_anomaly_detector(X_scaled)
        
        # Train health index model
        self.train_health_index_model(df)
        
        return True
    
    def save_model(self, model_dir='models'):
        """
        Save trained models to disk
        """
        Path(model_dir).mkdir(exist_ok=True)
        
        joblib.dump(self.rf_model, f'{model_dir}/health_model.pkl')
        joblib.dump(self.isolation_forest, f'{model_dir}/anomaly_model.pkl')
        joblib.dump(self.scaler, f'{model_dir}/scaler.pkl')
        
        print(f"Models saved to {model_dir}/")
    
    def load_model(self, model_dir='models'):
        """
        Load pre-trained models from disk
        """
        try:
            self.rf_model = joblib.load(f'{model_dir}/health_model.pkl')
            self.isolation_forest = joblib.load(f'{model_dir}/anomaly_model.pkl')
            self.scaler = joblib.load(f'{model_dir}/scaler.pkl')
            print(f"Models loaded from {model_dir}/")
            return True
        except FileNotFoundError:
            print(f"Models not found in {model_dir}/")
            return False


# Example usage
if __name__ == "__main__":
    analyzer = SoilHealthAnalyzer()
    
    # Train model
    if analyzer.train_on_csv('data/data.csv'):
        analyzer.save_model('models')
        
        # Test with sample reading
        test_reading = {
            'N': 22,
            'P': 18,
            'K': 150,
            'CO2': 500,
            'Temperature': 22,
            'Moisture': 55,
            'pH': 7.2
        }
        
        analysis = analyzer.analyze_reading(test_reading)
        print("\nSoil Health Analysis:")
        print(json.dumps(analysis, indent=2))
