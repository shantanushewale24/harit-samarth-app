"""
MQTT Subscriber - Subscribes to sensor data via MQTT
Receives sensor readings and stores them in CSV/Database
"""

import json
import csv
import time
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from pathlib import Path
import logging

from mqtt_config import (
    MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD,
    MQTT_TOPIC_SENSOR_DATA, MQTT_TOPIC_HEALTH_ANALYSIS, MQTT_TOPIC_STATUS,
    SUBSCRIBER_ID, SUBSCRIBER_DB_PATH
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MQTTSubscriber:
    """MQTT Subscriber for receiving sensor data"""
    
    def __init__(self, broker=MQTT_BROKER, port=MQTT_PORT,
                 username=MQTT_USERNAME, password=MQTT_PASSWORD,
                 subscriber_id=SUBSCRIBER_ID, db_path=SUBSCRIBER_DB_PATH):
        
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.subscriber_id = subscriber_id
        self.db_path = db_path
        
        self.client = mqtt.Client(client_id=subscriber_id)
        self.running = False
        self.messages_received = 0
        self.messages_stored = 0
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # Initialize CSV storage
        self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file for storing data"""
        Path("data").mkdir(exist_ok=True)
        
        if not Path(self.db_path).exists():
            try:
                with open(self.db_path, 'w', newline='') as f:
                    fieldnames = [
                        'timestamp', 'publisher_id',
                        'N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH',
                        'health_index', 'health_status', 'is_anomalous', 'anomaly_score'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                
                logger.info(f"✓ Created CSV database: {self.db_path}")
            
            except Exception as e:
                logger.error(f"❌ Failed to initialize CSV: {str(e)}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker"""
        if rc == 0:
            logger.info(f"🟢 Subscriber connected to MQTT broker at {self.broker}:{self.port}")
            
            # Subscribe to all relevant topics
            self.client.subscribe(MQTT_TOPIC_SENSOR_DATA, qos=1)
            self.client.subscribe(MQTT_TOPIC_HEALTH_ANALYSIS, qos=1)
            self.client.subscribe(MQTT_TOPIC_STATUS, qos=1)
            
            logger.info(f"📡 Subscribed to topics:")
            logger.info(f"   - {MQTT_TOPIC_SENSOR_DATA}")
            logger.info(f"   - {MQTT_TOPIC_HEALTH_ANALYSIS}")
            logger.info(f"   - {MQTT_TOPIC_STATUS}")
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker"""
        if rc != 0:
            logger.warning(f"⚠️  Unexpected disconnection with code {rc}")
        else:
            logger.info("🔴 Subscriber disconnected from MQTT broker")
    
    def on_message(self, client, userdata, msg):
        """Callback for when message is received"""
        try:
            self.messages_received += 1
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            logger.debug(f"📥 Message received on topic: {topic}")
            
            if topic == MQTT_TOPIC_SENSOR_DATA:
                self._handle_sensor_data(payload)
            
            elif topic == MQTT_TOPIC_HEALTH_ANALYSIS:
                self._handle_health_analysis(payload)
            
            elif topic == MQTT_TOPIC_STATUS:
                self._handle_status(payload)
        
        except json.JSONDecodeError:
            logger.error(f"❌ Failed to decode JSON message: {msg.payload}")
        
        except Exception as e:
            logger.error(f"❌ Error handling message: {str(e)}")
    
    def _handle_sensor_data(self, payload):
        """Handle incoming sensor data"""
        try:
            timestamp = payload.get('timestamp')
            publisher_id = payload.get('publisher_id')
            sensor_data = payload.get('sensor_data', {})
            
            logger.info(f"📊 Received sensor data from {publisher_id}")
            logger.info(f"   Timestamp: {timestamp}")
            logger.info(f"   Data: {sensor_data}")
            
            # Store in CSV
            self._save_to_csv(timestamp, publisher_id, sensor_data)
            
        except Exception as e:
            logger.error(f"❌ Error handling sensor data: {str(e)}")
    
    def _handle_health_analysis(self, payload):
        """Handle incoming health analysis results"""
        try:
            timestamp = payload.get('timestamp')
            publisher_id = payload.get('publisher_id')
            analysis = payload.get('analysis', {})
            
            logger.info(f"🏥 Received health analysis from {publisher_id}")
            logger.info(f"   Health Index: {analysis.get('soil_health_index')}/100")
            logger.info(f"   Status: {analysis.get('health_status')}")
            logger.info(f"   Anomaly: {analysis.get('is_anomalous')}")
            
            # Update existing record with analysis data
            self._update_csv_with_analysis(timestamp, publisher_id, analysis)
            
        except Exception as e:
            logger.error(f"❌ Error handling health analysis: {str(e)}")
    
    def _handle_status(self, payload):
        """Handle status messages"""
        try:
            status = payload.get('status')
            publisher_id = payload.get('publisher_id')
            
            logger.info(f"ℹ️  Status update from {publisher_id}: {status}")
        
        except Exception as e:
            logger.error(f"❌ Error handling status: {str(e)}")
    
    def _save_to_csv(self, timestamp, publisher_id, sensor_data):
        """Save sensor data to CSV"""
        try:
            with open(self.db_path, 'a', newline='') as f:
                row = {
                    'timestamp': timestamp,
                    'publisher_id': publisher_id,
                    'N': sensor_data.get('N'),
                    'P': sensor_data.get('P'),
                    'K': sensor_data.get('K'),
                    'CO2': sensor_data.get('CO2'),
                    'Temperature': sensor_data.get('Temperature'),
                    'Moisture': sensor_data.get('Moisture'),
                    'pH': sensor_data.get('pH'),
                    'health_index': '',
                    'health_status': '',
                    'is_anomalous': '',
                    'anomaly_score': ''
                }
                
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writerow(row)
            
            self.messages_stored += 1
            logger.info(f"✓ Stored sensor data (Total: {self.messages_stored})")
        
        except Exception as e:
            logger.error(f"❌ Error saving to CSV: {str(e)}")
    
    def _update_csv_with_analysis(self, timestamp, publisher_id, analysis):
        """Update CSV with health analysis data"""
        try:
            # Read all rows
            rows = []
            fieldnames = [
                'timestamp', 'publisher_id',
                'N', 'P', 'K', 'CO2', 'Temperature', 'Moisture', 'pH',
                'health_index', 'health_status', 'is_anomalous', 'anomaly_score'
            ]
            
            with open(self.db_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # Find and update the most recent row from this publisher
            found = False
            for row in reversed(rows):
                if row and row.get('publisher_id') == publisher_id:
                    row['health_index'] = str(analysis.get('soil_health_index', ''))
                    row['health_status'] = str(analysis.get('health_status', ''))
                    row['is_anomalous'] = str(analysis.get('is_anomalous', ''))
                    row['anomaly_score'] = str(analysis.get('anomaly_score', ''))
                    found = True
                    break
            
            # Write back all rows with fixed fieldnames
            if rows:
                with open(self.db_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                
                if found:
                    logger.info(f"✓ Updated record with health analysis")
                else:
                    logger.debug(f"ℹ️  No matching publisher record found for analysis update")
        
        except Exception as e:
            logger.error(f"❌ Error updating CSV: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
    
    def start(self):
        """Start listening for messages"""
        self.running = True
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 MQTT SUBSCRIBER STARTED")
        logger.info(f"{'='*70}")
        logger.info(f"Broker: {self.broker}:{self.port}")
        logger.info(f"Subscriber ID: {self.subscriber_id}")
        logger.info(f"Database Path: {self.db_path}")
        logger.info(f"{'='*70}\n")
    
    def get_stats(self):
        """Get subscriber statistics"""
        return {
            'messages_received': self.messages_received,
            'messages_stored': self.messages_stored,
            'database_path': self.db_path,
            'subscriber_id': self.subscriber_id
        }
    
    def stop(self):
        """Stop listening for messages"""
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("\n✓ MQTT Subscriber stopped")

def main():
    """Main entry point"""
    subscriber = MQTTSubscriber()
    
    try:
        # Connect to broker
        subscriber.connect()
        
        # Start listening
        subscriber.start()
        
        # Keep running and print stats periodically
        while subscriber.running:
            try:
                time.sleep(30)
                stats = subscriber.get_stats()
                logger.info(f"\n📊 Subscriber Stats:")
                logger.info(f"   Messages Received: {stats['messages_received']}")
                logger.info(f"   Messages Stored: {stats['messages_stored']}")
                logger.info(f"   Database: {stats['database_path']}\n")
            except Exception as e:
                logger.error(f"⚠️  Error in stats loop: {str(e)}")
                continue
    
    except KeyboardInterrupt:
        logger.info("\n\n✓ Shutting down subscriber...")
        subscriber.stop()
        logger.info("✓ Subscriber stopped gracefully")
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
