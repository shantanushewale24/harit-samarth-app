# Network Deployment Guide - Multi-Device Setup

## Architecture Overview

This guide explains how to run the Harit Samarth system across multiple devices on the same network.

```
DEVICE A (Publisher/Server)              DEVICE B (Receiver/Client)
├─ Backend API (Flask)                   ├─ Frontend (React) 
│  Port 5000                             │  Port 8080
├─ Sensor Generator                      │
│  Publishes data every 60s              │
├─ MQTT Broker (Mosquitto)               │
│  Port 1883                             │
└─ MySQL Database                        └─ Connects to Device A API
   Stores sensor readings                   Fetches: http://DEVICE_A_IP:5000

     ←────── MQTT/HTTP ────────→
```

## Prerequisites

**Device A (Publisher/Server)**:
- Python 3.8+
- MySQL 8.0+
- MQTT Broker (Mosquitto)
- Node.js (for building frontend if needed)

**Device B (Receiver/Client)**:
- Node.js 16+
- Web browser
- Network access to Device A

## Step 1: Find Your Device IPs

### On Windows (Device A - Publisher):
```powershell
# Open PowerShell and run:
ipconfig

# Look for your network adapter, find "IPv4 Address"
# Example output:
# IPv4 Address. . . . . . . . . . : 192.168.1.100
```

### On Linux/Mac:
```bash
ifconfig
# or
ip addr show
```

### Common IP Ranges:
- `192.168.1.x` - Home WiFi
- `192.168.0.x` - Corporate networks
- `10.0.x.x` - Larger networks

**Note down**: 
- Publisher/Server IP: `192.168.1.100` (example)
- Make sure both devices ping each other:
  ```powershell
  ping 192.168.1.100
  ```

## Step 2: Configure Publisher Device (Device A)

### 2.1 Set Environment Variables

**Windows PowerShell**:
```powershell
# Set the IP address of THIS device (publisher)
$env:MQTT_BROKER="192.168.1.100"
$env:MQTT_PORT="1883"
$env:BACKEND_API_URL="http://192.168.1.100:5000"

# Verify:
$env:MQTT_BROKER
```

**Linux/Mac Bash**:
```bash
export MQTT_BROKER="192.168.1.100"
export MQTT_PORT="1883"
export BACKEND_API_URL="http://192.168.1.100:5000"

# Verify:
echo $MQTT_BROKER
```

### 2.2 Start MQTT Broker

**Windows (with Mosquitto installed)**:
```powershell
# Ensure Mosquitto is listening on 0.0.0.0 (all interfaces)
mosquitto -v

# Or with configuration file:
mosquitto -c mosquitto.conf -v
```

**Linux**:
```bash
sudo mosquitto -v
# Or check service:
sudo systemctl status mosquitto
sudo systemctl start mosquitto
```

### 2.3 Start Backend Services

```powershell
# Terminal 1: Backend API
cd backend
$env:MQTT_BROKER="192.168.1.100"
$env:MQTT_PORT="1883"
$env:BACKEND_API_URL="http://192.168.1.100:5000"
python app.py

# Terminal 2: Sensor Generator
cd backend
$env:MQTT_BROKER="192.168.1.100"
$env:MQTT_PORT="1883"
python sensor_generator.py

# Terminal 3: MQTT Subscriber
cd backend
$env:MQTT_BROKER="192.168.1.100"
$env:MQTT_PORT="1883"
$env:BACKEND_API_URL="http://192.168.1.100:5000"
python mqtt_sensor_subscriber.py
```

### 2.4 Firewall Configuration

**Windows (allow other devices to connect)**:
```powershell
# Enable Flask API port
netsh advfirewall firewall add rule name="Harit Flask API" dir=in action=allow protocol=tcp localport=5000

# Enable MQTT port
netsh advfirewall firewall add rule name="Harit MQTT" dir=in action=allow protocol=tcp localport=1883

# Enable MySQL port (if needed)
netsh advfirewall firewall add rule name="Harit MySQL" dir=in action=allow protocol=tcp localport=3306
```

**Linux**:
```bash
sudo ufw allow 5000/tcp
sudo ufw allow 1883/tcp
sudo ufw allow 3306/tcp
sudo ufw reload
```

## Step 3: Configure Receiver Device (Device B)

### 3.1 Create `.env` File

In the frontend directory, create a `.env.local` file:

**For main app** (`harit-samarth-app/.env.local`):
```
VITE_BACKEND_API_URL=http://192.168.1.100:5000
```

**For smart-garden-hub** (`hardware module/smart-garden-hub/.env.local`):
```
VITE_BACKEND_API_URL=http://192.168.1.100:5000
```

Replace `192.168.1.100` with your actual publisher device IP!

### 3.2 Build/Run Frontend

```powershell
# Navigate to frontend directory
cd harit-samarth-app

# Install dependencies (first time only)
npm install

# Run development server
npm run dev

# Frontend will be available at: http://localhost:8080
```

### 3.3 Access Dashboard from Another Device

From **any device on the same network**:
1. Get the Device B IP (where frontend runs): `192.168.1.101`
2. Open browser and navigate to: `http://192.168.1.101:8080`
3. Dashboard will fetch data from Device A API automatically

## Step 4: Verify Network Connectivity

**From Device B (Receiver), test API connectivity**:

**PowerShell**:
```powershell
# Test if Device A API is reachable
curl http://192.168.1.100:5000/api/soil-health/latest

# Should return JSON sensor data
```

**Bash**:
```bash
curl http://192.168.1.100:5000/api/soil-health/latest
```

**Browser**:
- Navigate to: `http://192.168.1.100:5000/api/soil-health/latest`
- Should display JSON with sensor readings

## Troubleshooting

### Issue: "Connection refused" or "Network unreachable"

**Solution**:
1. Verify both devices are on same network:
   ```powershell
   ping 192.168.1.100
   ```

2. Check firewall allows port 5000:
   ```powershell
   netstat -ano | findstr :5000
   ```

3. Verify Flask is listening on all interfaces:
   - In `app.py`, ensure: `app.run(host='0.0.0.0', port=5000)`

### Issue: Frontend shows "Loading..." forever

**Solution**:
1. Check `.env.local` has correct IP:
   ```
   VITE_BACKEND_API_URL=http://192.168.1.100:5000
   ```

2. Check backend is running:
   ```powershell
   curl http://192.168.1.100:5000/api/soil-health/latest
   ```

3. Check browser console for error messages (F12 → Console)

### Issue: MQTT Broker not accessible

**Solution**:
1. Verify Mosquitto is running on 0.0.0.0:
   ```powershell
   netstat -ano | findstr :1883
   ```

2. Check firewall allows port 1883:
   ```powershell
   netsh advfirewall firewall show rule name="MQTT" verbose
   ```

## Advanced Configuration

### Using Online MQTT Broker

If devices can't connect to local MQTT:

```powershell
$env:MQTT_BROKER="broker.hivemq.com"  # or test.mosquitto.org
$env:MQTT_PORT="1883"
```

### Using Docker (Recommended for MQTT)

```bash
# Run Mosquitto in Docker
docker run -d -p 1883:1883 -p 9001:9001 eclipse-mosquitto
```

### Using HTTPS (Production)

```
# Use Caddy or nginx as reverse proxy
# Update frontend .env to use HTTPS:
VITE_BACKEND_API_URL=https://192.168.1.100:5000
```

## Security Best Practices

⚠️ **For Production Deployment**:

1. **Use MQTT Authentication**:
   - Add username/password to Mosquitto
   - Update connection strings

2. **Enable HTTPS**:
   - Use Let's Encrypt for certificates
   - Configure reverse proxy (nginx/Caddy)

3. **API Authentication**:
   - Add JWT tokens to Flask endpoints
   - Implement API key validation

4. **Network Segmentation**:
   - Use VPN for remote access
   - Implement firewall rules
   - Restrict to trusted devices only

5. **Database Security**:
   - Change default MySQL password
   - Use strong authentication
   - Enable SSL for MySQL connections

## Performance Notes

- **Latency**: ~100-200ms between devices (typical LAN)
- **Bandwidth**: <1 Mbps for sensor data
- **Polling Interval**: 10 seconds (configurable)
- **Sensor Generation**: Every 60 seconds

---

## Quick Reference

| Component | Port | Protocol |
|-----------|------|----------|
| Flask API | 5000 | HTTP/HTTPS |
| MQTT Broker | 1883 | MQTT |
| MySQL | 3306 | TCP |
| Frontend (Dev) | 8080 | HTTP |
| Frontend (Production) | 3000 | HTTP |

## Environment Variables

| Variable | Default | Example |
|----------|---------|---------|
| `VITE_BACKEND_API_URL` | http://localhost:5000 | http://192.168.1.100:5000 |
| `MQTT_BROKER` | localhost | 192.168.1.100 |
| `MQTT_PORT` | 1883 | 1883 |
| `BACKEND_API_URL` | http://localhost:5000 | http://192.168.1.100:5000 |

---

**Status**: ✅ Network deployment ready!

Your system is now configured for multi-device deployment with separate publisher and receiver capabilities.
