"""
MQTT Publisher - Publishes sensor data via MQTT
Generates sensor readings and publishes them to MQTT topics
"""

import json
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import random
from pathlib import Path
import csv
import logging

from mqtt_config import (
    MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD,
    MQTT_TOPIC_SENSOR_DATA, MQTT_TOPIC_HEALTH_ANALYSIS, MQTT_TOPIC_STATUS,
    PUBLISHER_ID, PUBLISH_INTERVAL
)

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

# Variation ranges
VARIATIONS = {
    'N': (-2, 2),
    'P': (-1, 1),
    'K': (-10, 10),
    'CO2': (-50, 50),
    'Temperature': (-2, 2),
    'Moisture': (-5, 5),
    'pH': (-0.3, 0.3)
}

class MQTTPublisher:
    """MQTT Publisher for sensor data"""
    
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT, 
                 username=MQTT_USERNAME, password=MQTT_PASSWORD,
                 publisher_id=PUBLISHER_ID, interval=PUBLISH_INTERVAL):
        
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.publisher_id = publisher_id
        self.interval = interval
        
        self.client = mqtt.Client(client_id=publisher_id)
        self.running = False
        self.last_reading = BASE_READINGS.copy()
        self.readings_count = 0
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
        # Create data directory
        Path("data").mkdir(exist_ok=True)
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker"""
        if rc == 0:
            logger.info(f"🟢 Publisher connected to MQTT broker at {self.broker}:{self.port}")
            self.client.publish(MQTT_TOPIC_STATUS, 
                              json.dumps({"status": "connected", "publisher_id": self.publisher_id}),
                              qos=1, retain=True)
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker"""
        if rc != 0:
            logger.warning(f"⚠️  Unexpected disconnection with code {rc}")
        else:
            logger.info("🔴 Publisher disconnected from MQTT broker")
    
    def on_publish(self, client, userdata, mid):
        """Callback for when message is published"""
        logger.debug(f"✓ Message published with ID {mid}")
    
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
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            logger.info(f"📡 Connecting to MQTT broker: {self.broker}:{self.port}...")
            time.sleep(2)  # Wait for connection
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MQTT broker: {str(e)}")
            raise
    
    def publish_sensor_data(self, reading):
        """Publish sensor reading to MQTT"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "publisher_id": self.publisher_id,
                "sensor_data": reading
            }
            
            topic = MQTT_TOPIC_SENSOR_DATA
            self.client.publish(topic, json.dumps(payload), qos=1, retain=False)
            
            self.readings_count += 1
            logger.info(f"📤 Published reading #{self.readings_count}")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Data: {reading}")
            
            return payload
            
        except Exception as e:
            logger.error(f"❌ Failed to publish: {str(e)}")
            return None
    
    def publish_health_analysis(self, analysis):
        """Publish health analysis results to MQTT"""
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "publisher_id": self.publisher_id,
                "analysis": analysis
            }
            
            topic = MQTT_TOPIC_HEALTH_ANALYSIS
            self.client.publish(topic, json.dumps(payload), qos=1, retain=False)
            
            logger.info(f"📤 Published health analysis")
            logger.info(f"   Health Index: {analysis.get('soil_health_index')}/100")
            logger.info(f"   Status: {analysis.get('health_status')}")
            
            return payload
            
        except Exception as e:
            logger.error(f"❌ Failed to publish analysis: {str(e)}")
            return None
    
    def start(self):
        """Start publishing sensor data"""
        self.running = True
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 MQTT PUBLISHER STARTED")
        logger.info(f"{'='*70}")
        logger.info(f"Broker: {self.broker}:{self.port}")
        logger.info(f"Publisher ID: {self.publisher_id}")
        logger.info(f"Sensor Topic: {MQTT_TOPIC_SENSOR_DATA}")
        logger.info(f"Health Topic: {MQTT_TOPIC_HEALTH_ANALYSIS}")
        logger.info(f"Publish Interval: {self.interval} seconds")
        logger.info(f"{'='*70}\n")
        
        # Start publishing in background thread
        thread = threading.Thread(target=self._publishing_loop, daemon=True)
        thread.start()
        
        return thread
    
    def _publishing_loop(self):
        """Main publishing loop"""
        while self.running:
            try:
                # Generate reading
                reading = self.generate_reading()
                
                # Publish sensor data
                self.publish_sensor_data(reading)
                
                # Simulate health analysis (in real scenario, this comes from backend API)
                analysis = self._simulate_health_analysis(reading)
                if analysis:
                    self.publish_health_analysis(analysis)
                
                # Wait for next interval
                next_publish = datetime.now() + timedelta(seconds=self.interval)
                logger.info(f"⏱️  Next reading at: {next_publish.strftime('%H:%M:%S')}\n")
                time.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"❌ Error in publishing loop: {str(e)}")
                time.sleep(5)
    
    def _simulate_health_analysis(self, reading):
        """Simulate health analysis (in production, call backend API)"""
        try:
            # Simple health score calculation
            score = 0
            weights = {
                'N': (15, 30, 1.0),
                'P': (10, 25, 1.0),
                'K': (100, 200, 1.0),
                'CO2': (400, 600, 0.8),
                'Temperature': (15, 25, 0.9),
                'Moisture': (40, 60, 1.0),
                'pH': (6.5, 7.5, 1.0)
            }
            
            total_weight = 0
            for param, (min_val, max_val, weight) in weights.items():
                value = reading.get(param.lower() if param != 'CO2' else 'CO2')
                if value is not None:
                    if min_val <= value <= max_val:
                        score += 100 * weight
                    else:
                        ratio = (value - min_val) / (max_val - min_val)
                        score += max(0, 100 - abs(ratio - 1) * 100) * weight
                    total_weight += weight
            
            health_index = round(score / total_weight if total_weight > 0 else 0)
            
            # Determine health status
            if health_index >= 80:
                health_status = "Excellent"
            elif health_index >= 60:
                health_status = "Good"
            elif health_index >= 40:
                health_status = "Fair"
            else:
                health_status = "Poor"
            
            return {
                "soil_health_index": health_index,
                "health_status": health_status,
                "is_anomalous": random.random() < 0.1,
                "anomaly_score": round(random.random(), 3)
            }
        
        except Exception as e:
            logger.error(f"❌ Error in health analysis: {str(e)}")
            return None
    
    def stop(self):
        """Stop publishing sensor data"""
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("\n✓ MQTT Publisher stopped")

def main():
    """Main entry point"""
    publisher = MQTTPublisher()
    
    try:
        # Connect to broker
        publisher.connect()
        
        # Start publishing
        thread = publisher.start()
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\n\n✓ Shutting down publisher...")
        publisher.stop()
        logger.info("✓ Publisher stopped gracefully")
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
