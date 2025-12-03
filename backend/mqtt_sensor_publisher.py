"""
MQTT Sensor Publisher
Publishes sensor data via MQTT to be consumed by backend subscriber
Replaces direct API calls with MQTT pub/sub architecture
Network-aware: Can run on any device and publish to brokers on the network
"""

import json
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import random
from pathlib import Path
import logging
import socket
import os

# MQTT Configuration - Network Aware
# Get from environment variables or use defaults
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_SENSOR_DATA = "harit-samarth/sensor/data"

# Backend API Configuration - Network Aware
API_URL = os.getenv("BACKEND_API_URL", "http://localhost:5000/api/soil-health/analyze")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

class MQTTSensorPublisher:
    """Publishes sensor data via MQTT instead of directly to API"""
    
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, interval=60):
        self.broker = broker
        self.port = port
        self.interval = interval
        self.running = False
        self.last_reading = BASE_READINGS.copy()
        self.readings_count = 0
        
        # MQTT client setup
        self.client = mqtt.Client(client_id="sensor-publisher-01")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        self.connected = False
        
        # Load historical data on startup
        self._load_historical_data()
    
    def _load_historical_data(self):
        """Load last reading from historical data if available"""
        try:
            csv_path = "data/sensor_readings.csv"
            if Path(csv_path).exists():
                with open(csv_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # Has data beyond header
                        last_line = lines[-1].strip()
                        values = last_line.split(',')
                        if len(values) >= 8:
                            try:
                                self.last_reading = {
                                    'N': float(values[1]),
                                    'P': float(values[2]),
                                    'K': float(values[3]),
                                    'CO2': float(values[4]),
                                    'Temperature': float(values[5]),
                                    'Moisture': float(values[6]),
                                    'pH': float(values[7])
                                }
                                print(f"✓ Loaded historical data from CSV")
                                print(f"  Last reading: N={self.last_reading['N']}, P={self.last_reading['P']}, K={self.last_reading['K']}")
                            except (ValueError, IndexError):
                                print(f"✓ Using default BASE_READINGS")
        except Exception as e:
            logger.debug(f"Could not load historical data: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when publisher connects to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"✓ MQTT Publisher connected to broker at {self.broker}:{self.port}")
        else:
            self.connected = False
            logger.error(f"✗ MQTT connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when publisher disconnects from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠ Unexpected MQTT disconnection with code {rc}")
    
    def on_publish(self, client, userdata, mid):
        """Callback for when message is published"""
        logger.debug(f"Message published with ID {mid}")
    
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
    
    def publish_reading(self, reading):
        """Publish sensor reading to MQTT topic"""
        try:
            # Create message with timestamp
            message = {
                'timestamp': datetime.now().isoformat(),
                'publisher_id': 'sensor-publisher-01',
                'sensor_readings': reading
            }
            
            # Publish to MQTT
            payload = json.dumps(message)
            result = self.client.publish(
                MQTT_TOPIC_SENSOR_DATA, 
                payload, 
                qos=1  # Quality of Service level 1 (at least once)
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"✓ Published reading to {MQTT_TOPIC_SENSOR_DATA}")
                return True
            else:
                logger.error(f"✗ Failed to publish: {mqtt.error_string(result.rc)}")
                return False
        
        except Exception as e:
            logger.error(f"✗ Error publishing reading: {str(e)}")
            return False
    
    def start(self):
        """Start sensor data publishing"""
        self.running = True
        
        # Try to connect to MQTT broker
        if not self.connect():
            logger.warning("⚠ Could not connect to MQTT broker, falling back to direct API mode")
            return None
        
        print(f"\n{'='*60}")
        print(f"  MQTT SENSOR PUBLISHER STARTED")
        print(f"{'='*60}")
        print(f"MQTT Broker: {self.broker}:{self.port}")
        print(f"Topic: {MQTT_TOPIC_SENSOR_DATA}")
        print(f"Update Interval: {self.interval} seconds")
        print(f"{'='*60}\n")
        
        # Start publishing in background thread
        thread = threading.Thread(target=self._publish_loop, daemon=True)
        thread.start()
        
        return thread
    
    def _publish_loop(self):
        """Main publishing loop"""
        while self.running:
            try:
                # Generate reading
                self.readings_count += 1
                reading = self.generate_reading()
                
                # Publish to MQTT
                if self.connected:
                    success = self.publish_reading(reading)
                    
                    if success:
                        print(f"\n✓ Reading #{self.readings_count}")
                        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"  N={reading['N']}, P={reading['P']}, K={reading['K']}")
                        print(f"  Temperature={reading['Temperature']}°C, Moisture={reading['Moisture']}%")
                    else:
                        logger.warning("⚠ Failed to publish reading")
                else:
                    logger.warning("⚠ MQTT not connected, skipping publish")
                
                # Calculate next update time
                next_update = datetime.now() + timedelta(seconds=self.interval)
                print(f"  Next reading at: {next_update.strftime('%H:%M:%S')}")
                
                # Wait for next update
                time.sleep(self.interval)
            
            except Exception as e:
                logger.error(f"✗ Error in publish loop: {str(e)}")
                import traceback
                traceback.print_exc()
                time.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Stop publishing"""
        self.running = False
        self.disconnect()
        print("\n✓ MQTT sensor publisher stopped")

def main():
    """Main entry point"""
    publisher = MQTTSensorPublisher(interval=60)
    
    try:
        # Start publisher
        thread = publisher.start()
        
        if thread is None:
            logger.error("Failed to start publisher")
            return
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
        publisher.stop()
        if thread:
            thread.join(timeout=5)
        print("✓ Publisher stopped")

if __name__ == '__main__':
    main()
