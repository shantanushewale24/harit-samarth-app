# MQTT Quick Start Guide

Your MQTT infrastructure is ready! Here's how to get it running:

## Step 1: Install Mosquitto MQTT Broker

**Windows (using Chocolatey):**
```powershell
choco install mosquitto
```

**Windows (manual download):**
Download from: https://mosquitto.org/download/

**macOS:**
```bash
brew install mosquitto
brew services start mosquitto
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mosquitto
sudo systemctl start mosquitto
```

## Step 2: Verify Installation

```powershell
mosquitto -v
```

Should show version info like: `mosquitto version 2.0.x running`

## Step 3: Start MQTT Broker (Terminal 1)

```powershell
mosquitto
```

Expected output:
```
1701547200: mosquitto version 2.0.x starting
1701547200: Using default config from C:\Program Files\mosquitto\mosquitto.conf
1701547200: Opening ipv4 listen socket on port 1883.
```

## Step 4: Run MQTT Publisher (Terminal 2)

Navigate to project root and activate venv:
```powershell
cd c:\Users\tanma\Downloads\harit-samarth-app-1\harit-samarth-app-1
.\venv\Scripts\Activate.ps1
```

Then run publisher:
```powershell
python backend\mqtt_publisher.py
```

Expected output:
```
INFO:__main__:🟢 Publisher connected to mqtt.localhost:1883
INFO:__main__:📤 Publishing sensor reading #1
INFO:__main__:📊 Health status: 65/100 (Good)
...
```

## Step 5: Run MQTT Subscriber (Terminal 3)

In a new terminal:
```powershell
cd c:\Users\tanma\Downloads\harit-samarth-app-1\harit-samarth-app-1
.\venv\Scripts\Activate.ps1
```

Then run subscriber:
```powershell
python backend\mqtt_subscriber.py
```

Expected output:
```
INFO:__main__:🟢 Subscriber connected to mqtt.localhost:1883
INFO:__main__:📊 Received sensor data from publisher-1
INFO:__main__:✓ Stored sensor data to CSV
...
```

## Step 6: Monitor Data

Check the CSV file for incoming data:
```powershell
Get-Content data\mqtt_sensor_data.csv | Select-Object -Last 5
```

Should show new rows with sensor readings every 60 seconds.

## Terminal Layout

```
┌─────────────────────────────────────┐
│  Terminal 1: MQTT Broker            │
│  $ mosquitto                        │
│  Listening on port 1883             │
└─────────────────────────────────────┘
         ↑              ↑
         │              │
    Publisher       Subscriber
         ↑              ↑
┌─────────────────────────────────────┐
│  Terminal 2: Publisher              │
│  $ python mqtt_publisher.py         │
│  Publishing data every 60 sec       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Terminal 3: Subscriber             │
│  $ python mqtt_subscriber.py        │
│  Storing data to CSV                │
└─────────────────────────────────────┘
```

## Files Created

- `backend/mqtt_config.py` - Shared configuration
- `backend/mqtt_publisher.py` - Publisher node
- `backend/mqtt_subscriber.py` - Subscriber node
- `data/mqtt_sensor_data.csv` - Data storage (auto-created)

## MQTT Topics

Data flows through these topics:

```
harit-samarth/
├── sensor/data              ← Raw sensor readings (N, P, K, CO2, Temp, Moisture, pH)
├── soil-health/analysis     ← Health analysis (health_index, status, anomaly_score)
└── status/                  ← Publisher status messages
```

## Troubleshooting

**Issue: "Connection refused" error**
- Make sure `mosquitto` is running in Terminal 1
- Check firewall isn't blocking port 1883

**Issue: "ModuleNotFoundError: No module named 'paho'"**
- Run: `.\venv\Scripts\pip install paho-mqtt`

**Issue: No data appearing in CSV**
- Check that all 3 terminals are running
- Verify CSV is in `data/mqtt_sensor_data.csv`
- Wait 60+ seconds for first data to appear

**Issue: "Address already in use"**
- Another MQTT broker is running on port 1883
- Kill the process: `Get-Process | Where-Object {$_.Name -eq "mosquitto"} | Stop-Process`

## Expected Data Structure

CSV file has 13 columns:
```
timestamp, publisher_id, N, P, K, CO2, Temperature, Moisture, pH, 
health_index, health_status, anomaly_score, critical_factors
```

Example row:
```
2025-12-02 18:08:24, publisher-1, 22.5, 18.2, 150.3, 502, 22.1, 55.2, 7.2, 65, Good, 0.018, Moisture
```

## Next Steps

1. ✅ Install Mosquitto
2. ✅ Start broker (Terminal 1)
3. ✅ Start publisher (Terminal 2)
4. ✅ Start subscriber (Terminal 3)
5. 📊 Monitor data in `data/mqtt_sensor_data.csv`
6. 📡 Integrate with React frontend when ready

## Integration with Flask Backend

The existing Flask backend (`app.py`) is already running on port 5000 and can:
- Analyze the CSV data stored by the subscriber
- Provide API endpoints for the frontend
- Generate crop recommendations based on sensor data

Your MQTT system feeds data → CSV → Flask API → React Frontend

Happy IoT farming! 🌾
