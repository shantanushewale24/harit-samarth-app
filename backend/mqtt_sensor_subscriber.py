"""
MQTT Subscriber Backend
Receives sensor data from MQTT publisher and processes it through the API
Stores data to MySQL and CSV
Network-aware: Can connect to MQTT brokers anywhere on the network
"""

import json
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from pathlib import Path
import logging
import requests
import csv
import os

# MQTT Configuration - Network Aware
# Get from environment variables or use defaults
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_SENSOR_DATA = "harit-samarth/sensor/data"

# Backend API Configuration - Network Aware
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:5000")
API_URL = f"{BACKEND_API_URL}/api/soil-health/analyze"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MQTTSensorSubscriber:
    """Subscribes to MQTT sensor data and forwards to API"""
    
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, api_url=API_URL):
        self.broker = broker
        self.port = port
        self.api_url = api_url
        self.running = False
        
        # MQTT client setup
        self.client = mqtt.Client(client_id="sensor-subscriber-01")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        self.connected = False
        self.messages_received = 0
        self.messages_processed = 0
        self.messages_failed = 0
        
        # Initialize data storage
        self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file for MQTT received data"""
        Path("data").mkdir(exist_ok=True)
        csv_path = "data/mqtt_sensor_received.csv"
        
        if not Path(csv_path).exists():
            try:
                with open(csv_path, 'w', newline='') as f:
                    fieldnames = [
                        'timestamp', 'publisher_id',
                        'N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH',
                        'health_index', 'health_status', 'is_anomalous', 'anomaly_score'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                
                logger.info(f"✓ Created MQTT CSV storage: {csv_path}")
            
            except Exception as e:
                logger.error(f"✗ Failed to initialize CSV: {str(e)}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when subscriber connects to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"✓ MQTT Subscriber connected to broker at {self.broker}:{self.port}")
            
            # Subscribe to sensor data topic
            client.subscribe(MQTT_TOPIC_SENSOR_DATA)
            logger.info(f"✓ Subscribed to topic: {MQTT_TOPIC_SENSOR_DATA}")
        else:
            self.connected = False
            logger.error(f"✗ MQTT connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when subscriber disconnects from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠ Unexpected MQTT disconnection with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback for when subscriber receives MQTT message"""
        try:
            self.messages_received += 1
            
            # Parse MQTT message
            payload = json.loads(msg.payload.decode('utf-8'))
            
            logger.debug(f"📨 Received MQTT message #{self.messages_received}")
            logger.debug(f"   Topic: {msg.topic}")
            logger.debug(f"   Payload: {payload}")
            
            # Extract sensor readings
            sensor_readings = payload.get('sensor_readings', {})
            timestamp = payload.get('timestamp', datetime.now().isoformat())
            publisher_id = payload.get('publisher_id', 'unknown')
            
            # Validate sensor readings
            required_fields = ['N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH']
            if not all(field in sensor_readings for field in required_fields):
                logger.warning(f"⚠ Invalid sensor readings format, skipping")
                self.messages_failed += 1
                return
            
            # Forward to API for analysis and storage
            success = self._process_via_api(sensor_readings)
            
            if success:
                self.messages_processed += 1
                # Store in CSV for record
                self._save_to_csv(timestamp, publisher_id, sensor_readings)
                print(f"\n✓ MQTT Message #{self.messages_received}")
                print(f"  Time: {timestamp}")
                print(f"  N={sensor_readings['N']}, P={sensor_readings['P']}, K={sensor_readings['K']}")
            else:
                self.messages_failed += 1
                logger.error(f"✗ Failed to process message via API")
        
        except json.JSONDecodeError as e:
            logger.error(f"✗ Failed to parse MQTT payload: {str(e)}")
            self.messages_failed += 1
        except Exception as e:
            logger.error(f"✗ Error processing MQTT message: {str(e)}")
            import traceback
            traceback.print_exc()
            self.messages_failed += 1
    
    def _process_via_api(self, sensor_readings):
        """Send sensor readings to API for analysis and storage"""
        try:
            response = requests.post(self.api_url, json=sensor_readings, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"  Health Index: {data['soil_health_index']}/100 ({data['health_status']})")
                if data.get('critical_factors'):
                    logger.info(f"  Critical Factors: {', '.join(data['critical_factors'])}")
                return True
            else:
                logger.error(f"✗ API Error: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ API Connection Error: {str(e)}")
            return False
    
    def _save_to_csv(self, timestamp, publisher_id, sensor_readings):
        """Save received message to CSV for audit trail"""
        try:
            csv_path = "data/mqtt_sensor_received.csv"
            
            with open(csv_path, 'a', newline='') as f:
                row = {
                    'timestamp': timestamp,
                    'publisher_id': publisher_id,
                    'N': sensor_readings.get('N', ''),
                    'P': sensor_readings.get('P', ''),
                    'K': sensor_readings.get('K', ''),
                    'CO2': sensor_readings.get('CO2', ''),
                    'Temperature': sensor_readings.get('Temperature', ''),
                    'Moisture': sensor_readings.get('Moisture', ''),
                    'pH': sensor_readings.get('pH', ''),
                    'health_index': '',  # Will be filled by API
                    'health_status': '',
                    'is_anomalous': '',
                    'anomaly_score': ''
                }
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writerow(row)
        
        except Exception as e:
            logger.error(f"✗ CSV save error: {str(e)}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()  # Start network loop in background
            
            # Wait for connection
            timeout = 10
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info("✓ Connected to MQTT broker")
                return True
            else:
                logger.error("✗ Failed to connect to MQTT broker within timeout")
                return False
        
        except Exception as e:
            logger.error(f"✗ MQTT connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("✓ Disconnected from MQTT broker")
        except Exception as e:
            logger.error(f"✗ Disconnection error: {str(e)}")
    
    def start(self):
        """Start subscriber"""
        self.running = True
        
        # Try to connect to MQTT broker
        if not self.connect():
            logger.error("✗ Could not connect to MQTT broker")
            return None
        
        print(f"\n{'='*60}")
        print(f"  MQTT SENSOR SUBSCRIBER STARTED")
        print(f"{'='*60}")
        print(f"MQTT Broker: {self.broker}:{self.port}")
        print(f"Topic: {MQTT_TOPIC_SENSOR_DATA}")
        print(f"API Endpoint: {self.api_url}")
        print(f"{'='*60}\n")
        
        # Keep running (network loop is already started in connect())
        self._monitor_loop()
        
        return True
    
    def _monitor_loop(self):
        """Monitor loop to print statistics"""
        while self.running:
            try:
                time.sleep(30)  # Print stats every 30 seconds
                print(f"\n📊 MQTT Subscriber Stats:")
                print(f"  Messages Received: {self.messages_received}")
                print(f"  Messages Processed: {self.messages_processed}")
                print(f"  Messages Failed: {self.messages_failed}")
                if self.messages_received > 0:
                    success_rate = (self.messages_processed / self.messages_received) * 100
                    print(f"  Success Rate: {success_rate:.1f}%")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"✗ Monitor loop error: {str(e)}")
    
    def stop(self):
        """Stop subscriber"""
        self.running = False
        self.disconnect()
        print("\n✓ MQTT sensor subscriber stopped")

def main():
    """Main entry point"""
    subscriber = MQTTSensorSubscriber(broker=MQTT_BROKER, port=MQTT_PORT, api_url=API_URL)
    
    try:
        # Start subscriber
        subscriber.start()
    
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
        subscriber.stop()
        print("✓ Subscriber stopped")
        print(f"\n📊 Final Stats:")
        print(f"  Total Received: {subscriber.messages_received}")
        print(f"  Successfully Processed: {subscriber.messages_processed}")
        print(f"  Failed: {subscriber.messages_failed}")

if __name__ == '__main__':
    main()
