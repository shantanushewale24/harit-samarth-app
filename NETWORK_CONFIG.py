# NETWORK CONFIGURATION
# Configure these values for your network setup

# ===== PUBLISHER DEVICE (Server) =====
# This is the device that runs the sensor generator/publisher

# Local IP of the publisher device (where the backend API runs)
# Get this from: ipconfig (Windows) or ifconfig (Linux/Mac)
# Example: 192.168.1.100 (replace with your actual IP)
PUBLISHER_IP = "192.168.1.100"
PUBLISHER_PORT = 5000

# MQTT Broker Configuration
# Option 1: Local Mosquitto on publisher device
MQTT_BROKER_IP = "192.168.1.100"  # Same as PUBLISHER_IP if running locally
MQTT_BROKER_PORT = 1883

# Option 2: Online MQTT Broker (if using cloud MQTT)
# Uncomment below and comment out Option 1
# MQTT_BROKER_IP = "broker.hivemq.com"  # or "test.mosquitto.org"
# MQTT_BROKER_PORT = 1883

# MQTT Topic for sensor data
MQTT_TOPIC = "harit-samarth/sensor/data"

# ===== FRONTEND DEVICE (Client/Receiver) =====
# This is the device that runs the React app and displays data

# The frontend will connect to the publisher device using this URL
# Replace with publisher device's actual IP address on the network
BACKEND_API_URL = "http://192.168.1.100:5000"  # Change 192.168.1.100 to actual publisher IP

# MQTT Connection for frontend (if using direct MQTT from browser)
# Most browsers can't connect to MQTT directly, so API is recommended
MQTT_BROKER_URL = "mqtt://192.168.1.100:1883"  # Change IP to MQTT broker IP

# ===== NETWORK SETUP GUIDE =====
"""
STEP 1: Find Publisher Device IP
   Windows:
   - Open Command Prompt
   - Run: ipconfig
   - Look for "IPv4 Address" under your network adapter
   - Example: 192.168.1.100

   Linux/Mac:
   - Open Terminal
   - Run: ifconfig or ip addr
   - Look for "inet" address
   - Example: 192.168.1.100

STEP 2: Update Configuration
   - Replace 192.168.1.100 with your actual publisher IP
   - Ensure both devices are on the same network
   - Test connectivity: ping 192.168.1.100

STEP 3: Start Publisher Device (Server)
   python mqtt_sensor_publisher.py
   python mqtt_sensor_subscriber.py  # If using MQTT mode
   python app.py  # Backend API

STEP 4: Start Frontend Device (Client)
   npm run dev
   Open: http://localhost:8080/hardware
   The frontend will fetch data from BACKEND_API_URL

STEP 5: Access from Other Device
   On any device on the same network:
   - Open browser
   - Navigate to: http://<frontend-device-ip>:8080
   - All data comes from the publisher device via API/MQTT
"""

# ===== IMPORTANT SECURITY NOTES =====
"""
⚠️ FOR PRODUCTION USE:
1. Use firewall rules to restrict access
2. Enable authentication on MQTT broker
3. Use TLS/SSL for all connections
4. Implement API authentication tokens
5. Don't expose to the internet without VPN/reverse proxy
6. Use environment variables for sensitive config

FIREWALL RULES (Windows):
   netsh advfirewall firewall add rule name="MQTT" dir=in action=allow protocol=tcp localport=1883
   netsh advfirewall firewall add rule name="Flask API" dir=in action=allow protocol=tcp localport=5000

FIREWALL RULES (Linux):
   sudo ufw allow 1883/tcp
   sudo ufw allow 5000/tcp
"""
