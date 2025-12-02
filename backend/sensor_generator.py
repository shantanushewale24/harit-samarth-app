"""
Real-time Sensor Data Generator
Generates realistic sensor data every minute and sends to API
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random
import threading
import csv
from pathlib import Path

# Configuration
API_URL = "http://localhost:5000/api/soil-health/analyze"
CSV_PATH = "data/sensor_readings.csv"
UPDATE_INTERVAL = 60  # Update every 60 seconds (1 minute)

# Base sensor reading
BASE_READINGS = {
    'N': 22,
    'P': 18,
    'K': 150,
    'CO2': 500,
    'Temperature': 22,
    'Moisture': 55,
    'pH': 7.2
}

# Variation ranges (simulate natural fluctuations)
VARIATIONS = {
    'N': (-2, 2),
    'P': (-1, 1),
    'K': (-10, 10),
    'CO2': (-50, 50),
    'Temperature': (-2, 2),
    'Moisture': (-5, 5),
    'pH': (-0.3, 0.3)
}

class SensorDataGenerator:
    """Generates and sends realistic sensor data"""
    
    def __init__(self, api_url=API_URL, csv_path=CSV_PATH, interval=UPDATE_INTERVAL):
        self.api_url = api_url
        self.csv_path = csv_path
        self.interval = interval
        self.running = False
        self.last_reading = BASE_READINGS.copy()
        self.readings_count = 0
        self.last_update_time = None
        
        # Create CSV file if it doesn't exist
        self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file with headers"""
        Path("data").mkdir(exist_ok=True)
        
        if not Path(self.csv_path).exists():
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH',
                    'health_index', 'health_status', 'is_anomalous', 'anomaly_score'
                ])
                writer.writeheader()
            print(f"✓ Created CSV file: {self.csv_path}")
    
    def generate_reading(self):
        """Generate next sensor reading with realistic variations"""
        reading = {}
        
        for param, value in self.last_reading.items():
            min_var, max_var = VARIATIONS[param]
            variation = random.uniform(min_var, max_var)
            new_value = value + variation
            
            # Add occasional spike (5% chance)
            if random.random() < 0.05:
                new_value = value + random.uniform(-30, 30)
            
            # Clamp to reasonable ranges
            if param == 'Temperature':
                new_value = max(5, min(35, new_value))
            elif param == 'Moisture':
                new_value = max(20, min(80, new_value))
            elif param == 'pH':
                new_value = max(4.0, min(9.0, new_value))
            elif param == 'CO2':
                new_value = max(300, min(1000, new_value))
            
            reading[param] = round(new_value, 2)
        
        self.last_reading = reading
        return reading
    
    def send_to_api(self, reading):
        """Send reading to backend API"""
        try:
            response = requests.post(self.api_url, json=reading, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Reading #{self.readings_count}")
                print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Health Index: {data['soil_health_index']}/100 ({data['health_status']})")
                print(f"  Anomaly: {data['is_anomalous']} (Score: {data['anomaly_score']:.3f})")
                if data['critical_factors']:
                    print(f"  Critical Factors: {', '.join(data['critical_factors'])}")
                
                return data
            else:
                print(f"✗ API Error: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection Error: {str(e)}")
            return None
    
    def save_to_csv(self, reading, analysis=None):
        """Save reading to CSV file"""
        try:
            with open(self.csv_path, 'a', newline='') as f:
                row = {
                    'timestamp': datetime.now().isoformat(),
                    'N': reading.get('N'),
                    'P': reading.get('P'),
                    'K': reading.get('K'),
                    'CO2': reading.get('CO2'),
                    'Temperature': reading.get('Temperature'),
                    'Moisture': reading.get('Moisture'),
                    'pH': reading.get('pH'),
                    'health_index': analysis.get('soil_health_index') if analysis else '',
                    'health_status': analysis.get('health_status') if analysis else '',
                    'is_anomalous': analysis.get('is_anomalous') if analysis else '',
                    'anomaly_score': analysis.get('anomaly_score') if analysis else ''
                }
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writerow(row)
        
        except Exception as e:
            print(f"✗ CSV Error: {str(e)}")
    
    def start(self):
        """Start generating sensor data"""
        self.running = True
        print(f"\n{'='*60}")
        print(f"  SENSOR DATA GENERATOR STARTED")
        print(f"{'='*60}")
        print(f"API URL: {self.api_url}")
        print(f"CSV Path: {self.csv_path}")
        print(f"Update Interval: {self.interval} seconds")
        print(f"{'='*60}\n")
        
        # Generate in background thread
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()
        
        return thread
    
    def _loop(self):
        """Main generation loop"""
        while self.running:
            try:
                # Generate reading
                self.readings_count += 1
                reading = self.generate_reading()
                
                # Send to API
                analysis = self.send_to_api(reading)
                
                # Save to CSV
                if analysis:
                    self.save_to_csv(reading, analysis)
                
                # Calculate next update time
                self.last_update_time = datetime.now()
                next_update = datetime.now() + timedelta(seconds=self.interval)
                
                # Wait for next update
                print(f"  Next reading at: {next_update.strftime('%H:%M:%S')}")
                time.sleep(self.interval)
            
            except Exception as e:
                print(f"✗ Error in generation loop: {str(e)}")
                import traceback
                traceback.print_exc()
                time.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Stop generating sensor data"""
        self.running = False
        print("\n✓ Sensor data generator stopped")

def main():
    """Main entry point"""
    generator = SensorDataGenerator()
    
    try:
        # Start generator
        thread = generator.start()
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
        generator.stop()
        thread.join(timeout=5)
        print("✓ Generator stopped")

if __name__ == '__main__':
    main()
