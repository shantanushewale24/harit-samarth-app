# MQTT Publisher & Subscriber Setup Guide

This guide explains how to use the MQTT Publisher and Subscriber for sensor data transmission in the Harit Samarth application.

## Overview

- **Publisher**: Generates sensor data and publishes it to MQTT topics
- **Subscriber**: Listens to MQTT topics and stores data in CSV
- **Protocol**: MQTT (lightweight IoT protocol)
- **Broker**: Mosquitto or any MQTT broker (default: localhost:1883)

## Architecture

```
┌─────────────────────┐
│  Sensor Generator   │
│   (Data Source)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐      MQTT      ┌─────────────────────┐
│  MQTT Publisher     │───────────────▶│  MQTT Subscriber    │
│  (Port 1883)        │                │  (Data Consumer)    │
└─────────────────────┘                └──────────┬──────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────────┐
                                        │  CSV Database       │
                                        │  mqtt_sensor_data   │
                                        └─────────────────────┘
```

## Installation

### 1. Install MQTT Broker (Mosquitto)

**Windows:**
```powershell
# Option 1: Using Chocolatey
choco install mosquitto

# Option 2: Download from
# https://mosquitto.org/download/
```

**macOS:**
```bash
brew install mosquitto
brew services start mosquitto
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

### 2. Install Python Dependencies

```powershell
cd "c:\Users\tanma\Downloads\harit-samarth-app-1\harit-samarth-app-1"
.\venv\Scripts\pip install paho-mqtt
```

Or update all requirements:
```powershell
.\venv\Scripts\pip install -r backend\requirements.txt
```

### 3. Start MQTT Broker

**Windows:**
```powershell
mosquitto -v
```

**macOS/Linux:**
```bash
mosquitto -c /etc/mosquitto/mosquitto.conf -v
```

You should see:
```
1670256000: mosquitto version 2.x.x starting
1670256000: Using default config from /etc/mosquitto/mosquitto.conf
1670256000: Opening ipv4 listen socket on port 1883.
```

## Configuration

Edit `mqtt_config.py` to customize settings:

```python
# MQTT Broker Configuration
MQTT_BROKER = "localhost"  # Your MQTT broker address
MQTT_PORT = 1883          # MQTT port (default: 1883)
MQTT_USERNAME = None      # Set if broker requires authentication
MQTT_PASSWORD = None      # Set if broker requires authentication

# MQTT Topics
MQTT_TOPIC_SENSOR_DATA = "harit-samarth/sensor/data"
MQTT_TOPIC_HEALTH_ANALYSIS = "harit-samarth/soil-health/analysis"
MQTT_TOPIC_STATUS = "harit-samarth/status"

# Intervals
PUBLISH_INTERVAL = 60  # Seconds between publications
```

## Running Publisher & Subscriber

### Terminal 1: Start MQTT Broker
```powershell
mosquitto -v
```

### Terminal 2: Start Publisher
```powershell
cd "c:\Users\tanma\Downloads\harit-samarth-app-1\harit-samarth-app-1"
.\venv\Scripts\python.exe backend\mqtt_publisher.py
```

**Expected Output:**
```
2025-12-02 18:15:30 - __main__ - INFO - 📡 Connecting to MQTT broker: localhost:1883...
2025-12-02 18:15:32 - __main__ - INFO - 🟢 Publisher connected to MQTT broker at localhost:1883
2025-12-02 18:15:32 - __main__ - INFO - ======================================================================
2025-12-02 18:15:32 - __main__ - INFO - 🚀 MQTT PUBLISHER STARTED
2025-12-02 18:15:32 - __main__ - INFO - ======================================================================
2025-12-02 18:15:32 - __main__ - INFO - Broker: localhost:1883
2025-12-02 18:15:32 - __main__ - INFO - Publisher ID: sensor-publisher-01
2025-12-02 18:15:32 - __main__ - INFO - Sensor Topic: harit-samarth/sensor/data
2025-12-02 18:15:32 - __main__ - INFO - Health Topic: harit-samarth/soil-health/analysis
2025-12-02 18:15:32 - __main__ - INFO - Publish Interval: 60 seconds
2025-12-02 18:15:32 - __main__ - INFO - ======================================================================
2025-12-02 18:15:33 - __main__ - INFO - 📤 Published reading #1
2025-12-02 18:15:33 - __main__ - INFO -    Topic: harit-samarth/sensor/data
2025-12-02 18:15:33 - __main__ - INFO -    Data: {'N': 22.5, 'P': 18.2, ...}
```

### Terminal 3: Start Subscriber
```powershell
cd "c:\Users\tanma\Downloads\harit-samarth-app-1\harit-samarth-app-1"
.\venv\Scripts\python.exe backend\mqtt_subscriber.py
```

**Expected Output:**
```
2025-12-02 18:15:40 - __main__ - INFO - 📡 Connecting to MQTT broker: localhost:1883...
2025-12-02 18:15:42 - __main__ - INFO - 🟢 Subscriber connected to MQTT broker at localhost:1883
2025-12-02 18:15:42 - __main__ - INFO - 📡 Subscribed to topics:
2025-12-02 18:15:42 - __main__ - INFO -    - harit-samarth/sensor/data
2025-12-02 18:15:42 - __main__ - INFO -    - harit-samarth/soil-health/analysis
2025-12-02 18:15:42 - __main__ - INFO -    - harit-samarth/status
2025-12-02 18:15:42 - __main__ - INFO - ======================================================================
2025-12-02 18:15:42 - __main__ - INFO - 🚀 MQTT SUBSCRIBER STARTED
2025-12-02 18:15:42 - __main__ - INFO - ======================================================================
2025-12-02 18:15:43 - __main__ - INFO - 📊 Received sensor data from sensor-publisher-01
2025-12-02 18:15:43 - __main__ - INFO -    Timestamp: 2025-12-02T18:15:43.123456
2025-12-02 18:15:43 - __main__ - INFO -    Data: {'N': 22.5, 'P': 18.2, ...}
2025-12-02 18:15:43 - __main__ - INFO - ✓ Stored sensor data (Total: 1)
```

## MQTT Message Format

### Sensor Data Message
**Topic:** `harit-samarth/sensor/data`

```json
{
  "timestamp": "2025-12-02T18:15:33.123456",
  "publisher_id": "sensor-publisher-01",
  "sensor_data": {
    "N": 22.5,
    "P": 18.2,
    "K": 155.3,
    "CO2": 520.1,
    "Temperature": 22.1,
    "Moisture": 55.3,
    "pH": 7.15
  }
}
```

### Health Analysis Message
**Topic:** `harit-samarth/soil-health/analysis`

```json
{
  "timestamp": "2025-12-02T18:15:35.123456",
  "publisher_id": "sensor-publisher-01",
  "analysis": {
    "soil_health_index": 75,
    "health_status": "Good",
    "is_anomalous": false,
    "anomaly_score": 0.05
  }
}
```

### Status Message
**Topic:** `harit-samarth/status`

```json
{
  "status": "connected",
  "publisher_id": "sensor-publisher-01"
}
```

## Data Storage

Received data is stored in: `data/mqtt_sensor_data.csv`

**Columns:**
- timestamp: When data was received
- publisher_id: Source of the data
- N, P, K, CO2, Temperature, Moisture, pH: Sensor readings
- health_index: Soil health index (0-100)
- health_status: Excellent/Good/Fair/Poor
- is_anomalous: Anomaly detection flag
- anomaly_score: Anomaly confidence score

## Monitoring Messages

### Using MQTT CLI (Option 1)

```powershell
# Subscribe to sensor data
mosquitto_sub -h localhost -p 1883 -t "harit-samarth/sensor/data" -v

# Subscribe to all topics
mosquitto_sub -h localhost -p 1883 -t "harit-samarth/#" -v
```

### Using Python Script (Option 2)

Create `monitor_mqtt.py`:
```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}")
    print(f"Payload: {json.dumps(json.loads(msg.payload), indent=2)}\n")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("harit-samarth/#")
client.loop_forever()
```

Run:
```powershell
.\venv\Scripts\python.exe monitor_mqtt.py
```

## Troubleshooting

### Issue: "Connection refused" (10061)

**Solution:**
1. Check if MQTT broker is running
2. Verify broker address and port in `mqtt_config.py`
3. Restart the broker

```powershell
# Windows
mosquitto -v

# Check listening ports
netstat -an | findstr "1883"
```

### Issue: "Unable to import paho.mqtt"

**Solution:**
```powershell
.\venv\Scripts\pip install paho-mqtt
```

### Issue: Publisher not sending data

**Solution:**
1. Check MQTT broker is running
2. Check firewall isn't blocking port 1883
3. Verify publisher can connect:
```powershell
# Test connection
python -c "import paho.mqtt.client as mqtt; print('MQTT module OK')"
```

### Issue: Subscriber not receiving data

**Solution:**
1. Start publisher BEFORE subscriber
2. Check both are connected to same broker
3. Verify topics match in `mqtt_config.py`
4. Check subscriber logs for errors

## Advanced Features

### 1. Remote MQTT Broker

For remote broker, update `mqtt_config.py`:
```python
MQTT_BROKER = "your-broker-address.com"
MQTT_PORT = 8883  # Port for remote broker
MQTT_USERNAME = "username"
MQTT_PASSWORD = "password"
```

### 2. Multiple Publishers

Create multiple instances with different IDs:
```python
publisher1 = MQTTPublisher(publisher_id="sensor-publisher-01")
publisher2 = MQTTPublisher(publisher_id="sensor-publisher-02")
```

### 3. Data Filtering

Modify subscriber to filter data:
```python
def _handle_sensor_data(self, payload):
    sensor_data = payload.get('sensor_data', {})
    
    # Only store if moisture is critical
    if sensor_data.get('Moisture', 0) < 30:
        self._save_to_csv(...)
```

## Integration with Web App

The stored CSV data can be used in the frontend:

```javascript
// Fetch MQTT data
fetch('http://localhost:5000/api/mqtt/latest')
  .then(res => res.json())
  .then(data => console.log(data))
```

## Performance Tips

1. **Increase QoS for reliability:**
   ```python
   self.client.publish(topic, payload, qos=2)  # Guaranteed delivery
   ```

2. **Batch messages for high frequency:**
   ```python
   PUBLISH_INTERVAL = 10  # Publish every 10 seconds
   ```

3. **Monitor memory:**
   - Keep MQTT history limited
   - Archive old CSV data periodically
   - Use database instead of CSV for large volumes

## Security Best Practices

1. **Use authentication:**
   ```python
   MQTT_USERNAME = "user"
   MQTT_PASSWORD = "secure-password"
   ```

2. **Use TLS/SSL:**
   ```python
   client.tls_set(ca_certs="ca.crt", certfile="client.crt", keyfile="client.key")
   ```

3. **Restrict topics:**
   - Publishers: Only `harit-samarth/sensor/*`
   - Subscribers: Only receive `harit-samarth/*`

## Next Steps

1. ✅ Start MQTT broker
2. ✅ Run publisher
3. ✅ Run subscriber
4. ✅ Monitor data in `data/mqtt_sensor_data.csv`
5. 🔄 Integrate with backend API
6. 🔄 Display in web frontend
7. 🔄 Add real sensor hardware integration

## Support

For issues or questions:
- Check logs in console output
- Review MQTT broker logs
- Verify network connectivity
- Ensure Python packages are installed

Happy IoT sensing! 🌱📊
