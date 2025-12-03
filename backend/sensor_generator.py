"""
Real-time Sensor Data Generator
Generates realistic sensor data every minute and publishes via MQTT
"""

import requests
import json
import time
from datetime import datetime, timedelta
import random
import threading
import csv
from pathlib import Path
import paho.mqtt.client as mqtt
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:5000/api/soil-health/analyze"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "harit-samarth/sensor/data"
CSV_PATH = "data/sensor_readings.csv"
UPDATE_INTERVAL = 60  # Update every 60 seconds (1 minute)
USE_MQTT = True  # Set to False to use direct API instead

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
    """Generates and sends realistic sensor data via MQTT or API"""
    
    def __init__(self, api_url=API_URL, mqtt_broker=MQTT_BROKER, mqtt_port=MQTT_PORT, 
                 mqtt_topic=MQTT_TOPIC, csv_path=CSV_PATH, interval=UPDATE_INTERVAL, use_mqtt=USE_MQTT):
        self.api_url = api_url
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.csv_path = csv_path
        self.interval = interval
        self.use_mqtt = use_mqtt
        
        self.running = False
        self.last_reading = BASE_READINGS.copy()
        self.readings_count = 0
        self.last_update_time = None
        
        # MQTT setup
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # Create CSV file if it doesn't exist
        self._init_csv()
        
        # Load historical data to seed the generator
        self._load_historical_data()
        
        # Initialize MQTT if enabled
        if self.use_mqtt:
            self._init_mqtt()
    
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
    
    def _load_historical_data(self):
        """Load last reading from API to seed generator with historical data"""
        try:
            # Get latest reading from backend API
            latest_url = "http://localhost:5000/api/soil-health/latest"
            
            # Retry a few times in case backend is starting up
            for attempt in range(3):
                try:
                    response = requests.get(latest_url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        last_reading = data.get('sensor_readings', {})
                        
                        if last_reading:
                            self.last_reading = {
                                'N': float(last_reading.get('N', BASE_READINGS['N'])),
                                'P': float(last_reading.get('P', BASE_READINGS['P'])),
                                'K': float(last_reading.get('K', BASE_READINGS['K'])),
                                'CO2': float(last_reading.get('CO2', BASE_READINGS['CO2'])),
                                'Temperature': float(last_reading.get('Temperature', BASE_READINGS['Temperature'])),
                                'Moisture': float(last_reading.get('Moisture', BASE_READINGS['Moisture'])),
                                'pH': float(last_reading.get('pH', BASE_READINGS['pH']))
                            }
                            print(f"✓ Loaded historical data from API")
                            print(f"  Last reading: N={self.last_reading['N']}, P={self.last_reading['P']}, K={self.last_reading['K']}")
                            return
                    elif response.status_code == 404:
                        # No data yet, use defaults
                        print(f"ℹ No historical data available (first run), using defaults")
                        return
                    else:
                        print(f"  Attempt {attempt+1}: API returned {response.status_code}, retrying...")
                        time.sleep(1)
                
                except requests.exceptions.RequestException as e:
                    if attempt < 2:
                        print(f"  Attempt {attempt+1}: Connection error, retrying... ({str(e)})")
                        time.sleep(1)
                    else:
                        print(f"✗ Failed to load historical data: {str(e)}")
                        print(f"✓ Using default BASE_READINGS, will start fresh")
        
        except Exception as e:
            print(f"✗ Error loading historical data: {str(e)}")
            print(f"✓ Using default BASE_READINGS")
    
    def _init_mqtt(self):
        """Initialize MQTT client"""
        try:
            self.mqtt_client = mqtt.Client(client_id="sensor-publisher-01")
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_publish = self._on_mqtt_publish
            
            print(f"Connecting to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}...")
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            self.mqtt_client.loop_start()  # Start MQTT network loop
            
            # Wait for connection
            timeout = 5
            start = time.time()
            while not self.mqtt_connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if self.mqtt_connected:
                print(f"✓ MQTT connected, will publish to {self.mqtt_topic}")
            else:
                print(f"⚠ MQTT connection timeout, will fall back to API")
                self.use_mqtt = False
        
        except Exception as e:
            print(f"⚠ MQTT initialization failed: {str(e)}")
            print(f"  Will fall back to API mode")
            self.use_mqtt = False
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            self.mqtt_connected = True
            print(f"✓ MQTT Publisher connected")
        else:
            self.mqtt_connected = False
            print(f"✗ MQTT connection failed: {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnect callback"""
        self.mqtt_connected = False
        if rc != 0:
            print(f"⚠ MQTT disconnected: {rc}")
    
    def _on_mqtt_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        pass  # Silent callback
    
    def _publish_via_mqtt(self, reading):
        """Publish sensor reading via MQTT"""
        try:
            if not self.mqtt_client or not self.mqtt_connected:
                return False
            
            message = {
                'timestamp': datetime.now().isoformat(),
                'publisher_id': 'sensor-publisher-01',
                'sensor_readings': reading
            }
            
            payload = json.dumps(message)
            result = self.mqtt_client.publish(self.mqtt_topic, payload, qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
            else:
                print(f"✗ MQTT publish failed: {mqtt.error_string(result.rc)}")
                return False
        
        except Exception as e:
            print(f"✗ MQTT publish error: {str(e)}")
            return False
    
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
        mode = "MQTT Publisher" if self.use_mqtt and self.mqtt_connected else "API Direct"
        
        print(f"\n{'='*60}")
        print(f"  SENSOR DATA GENERATOR STARTED")
        print(f"{'='*60}")
        print(f"Mode: {mode}")
        if self.use_mqtt:
            print(f"MQTT Broker: {self.mqtt_broker}:{self.mqtt_port}")
            print(f"Topic: {self.mqtt_topic}")
        else:
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
                
                # Send via MQTT or API
                if self.use_mqtt and self.mqtt_connected:
                    # Publish via MQTT (subscriber will handle API call)
                    success = self._publish_via_mqtt(reading)
                else:
                    # Fallback to direct API call
                    analysis = self.send_to_api(reading)
                    success = analysis is not None
                
                # Save to CSV
                if success:
                    if self.use_mqtt and self.mqtt_connected:
                        self.save_to_csv(reading, None)
                    else:
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
