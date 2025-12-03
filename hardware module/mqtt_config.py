"""
MQTT Configuration
Shared settings for publisher and subscriber
"""

# MQTT Broker Configuration
MQTT_BROKER = "localhost"  # Change to your MQTT broker address
MQTT_PORT = 1883           # Default MQTT port
MQTT_USERNAME = None       # Set if broker requires authentication
MQTT_PASSWORD = None       # Set if broker requires authentication

# MQTT Topics
MQTT_TOPIC_SENSOR_DATA = "harit-samarth/sensor/data"           # Raw sensor readings
MQTT_TOPIC_HEALTH_ANALYSIS = "harit-samarth/soil-health/analysis"  # Health analysis results
MQTT_TOPIC_STATUS = "harit-samarth/status"                     # System status messages

# Publisher Settings
PUBLISHER_ID = "sensor-publisher-01"
PUBLISH_INTERVAL = 60  # Publish every 60 seconds

# Subscriber Settings
SUBSCRIBER_ID = "data-subscriber-01"
SUBSCRIBER_DB_PATH = "data/mqtt_sensor_data.csv"

# Data Retention
DATA_RETENTION_DAYS = 30
