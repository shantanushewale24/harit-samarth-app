# MQTT Frontend Integration Guide

## Overview
This document explains how the MQTT IoT sensor data is integrated into the Harit Samarth frontend application.

## Architecture

### Data Flow
```
MQTT Publisher → Mosquitto Broker → MQTT Subscriber → CSV File
                                                        ↓
                                                  Backend API
                                                        ↓
                                                  Frontend React
```

## Frontend Integration

### 1. MQTT Service (`src/services/mqttService.ts`)

The MQTT service provides functions to fetch sensor data from the backend:

```typescript
// Fetch latest sensor reading
const data = await fetchLatestSensorData();

// Fetch all historical data
const allData = await fetchAllSensorData();

// Fetch data from last N minutes
const recentData = await fetchSensorDataByTime(60); // Last 60 minutes

// Stream real-time data (WebSocket)
const cleanup = streamMQTTData(
  (data) => console.log('New data:', data),
  (error) => console.error('Error:', error)
);
```

### 2. Hardware Module (`src/components/HardwareModule.tsx`)

Enhanced with MQTT data integration:

#### Features:
- **MQTT Connection**: Connect to MQTT brokers via WebSocket
- **CSV Data Loading**: Load latest MQTT data from CSV file
- **Real-time Display**: Show sensor readings with health status
- **Health Indicators**: Visual health index with progress bar
- **Environmental Sensors**: Display temperature, humidity, and CO₂ levels
- **Irrigation Control**: Remote actuator control via MQTT

#### Sensor Data Displayed:
```
Soil Sensors:
- Moisture (%)
- pH Level
- Nitrogen (mg/kg)
- Phosphorus (mg/kg)
- Potassium (mg/kg)

Environmental Sensors:
- Temperature (°C)
- Humidity (%)
- CO₂ Level (ppm)

Health Metrics:
- Health Index (0-100)
- Health Status (Excellent/Good/Poor)
```

### 3. Data Interface

```typescript
interface MQTTSensorData {
  timestamp: string;           // ISO 8601 timestamp
  publisherId: string;         // Sensor publisher ID
  nitrogen: number;            // mg/kg
  phosphorus: number;          // mg/kg
  potassium: number;           // mg/kg
  co2: number;                 // ppm
  temperature: number;         // °C
  moisture: number;            // %
  ph: number;                  // pH value
  healthIndex: number;         // 0-100
  healthStatus: string;        // Excellent/Good/Poor
  isAnomalous: boolean;        // Anomaly detection
  anomalyScore: number;        // 0-1 anomaly confidence
}
```

## Backend API Endpoints

### 1. Get Latest MQTT Data
```
GET /api/mqtt/latest
Response: MQTTSensorData
```

**Example Response:**
```json
{
  "timestamp": "2025-12-02T18:59:50.059843",
  "publisherId": "sensor-publisher-01",
  "nitrogen": 20.34,
  "phosphorus": 17.11,
  "potassium": 150.82,
  "co2": 494.31,
  "temperature": 21.94,
  "moisture": 53.78,
  "ph": 7.18,
  "healthIndex": 100,
  "healthStatus": "Excellent",
  "isAnomalous": false,
  "anomalyScore": 0.652
}
```

### 2. Get All MQTT Data
```
GET /api/mqtt/all
Response: MQTTSensorData[]
```

Returns all stored MQTT sensor readings.

### 3. Get MQTT Data by Time Range
```
GET /api/mqtt/data?minutes=60
Response: MQTTSensorData[]
```

Returns sensor data from the last N minutes.
- **Query Param**: `minutes` (default: 60)

## MQTT Configuration

### Broker Details
```
Host: localhost
Port: 1883
Protocol: mqtt://
```

### Topics Published

| Topic | Content | Frequency |
|-------|---------|-----------|
| `harit-samarth/sensor/data` | Raw sensor readings | 60 seconds |
| `harit-samarth/soil-health/analysis` | Health analysis data | 60 seconds |
| `harit-samarth/status` | Publisher status | 60 seconds |

### Message Format

**Sensor Data Topic:**
```json
{
  "nitrogen": 20.34,
  "phosphorus": 17.11,
  "potassium": 150.82,
  "co2": 494.31,
  "temperature": 21.94,
  "moisture": 53.78,
  "ph": 7.18
}
```

**Health Analysis Topic:**
```json
{
  "health_index": 100,
  "health_status": "Excellent",
  "is_anomalous": false,
  "anomaly_score": 0.652
}
```

## Running the System

### Prerequisites
1. **Mosquitto Broker** - MQTT message broker
2. **Backend Server** - Flask API serving data
3. **Frontend** - React app displaying data

### Step 1: Start MQTT Broker
```bash
mosquitto -v
# Port 1883 should be listening
```

### Step 2: Start MQTT Publisher
```bash
cd harit-samarth-app-1
python backend/mqtt_publisher.py
# Publishes sensor data every 60 seconds
```

### Step 3: Start MQTT Subscriber
```bash
cd harit-samarth-app-1
python run_subscriber_persistent.py
# Receives and stores data to CSV
```

### Step 4: Start Backend API
```bash
cd harit-samarth-app-1
python backend/app.py
# API server on http://localhost:5000
```

### Step 5: Start Frontend
```bash
cd harit-samarth-app-1
npm run dev
# Frontend on http://localhost:8080
```

## Using the Hardware Module

### Option 1: Direct MQTT Connection
1. Go to Hardware page
2. Enter MQTT Broker URL (default: `mqtt://broker.hivemq.com`)
3. Enter Topic (default: `agribio/sensors`)
4. Click "Connect to Hardware"
5. View real-time sensor data

### Option 2: Load from CSV
1. Go to Hardware page
2. Click "Load Latest CSV Data"
3. View latest sensor reading from MQTT system

### Data Updates
- **MQTT Connection**: Updates when broker publishes new data
- **CSV Loading**: Updates every time you click the button (manual refresh)
- **Auto-refresh**: Implement polling interval as needed

## CSV Storage Structure

**File**: `data/mqtt_sensor_data.csv`

**Columns:**
```
timestamp,publisher_id,nitrogen,phosphorus,potassium,co2,temperature,moisture,pH,health_index,health_status,is_anomalous,anomaly_score
```

**Example Data:**
```
2025-12-02T18:50:36.562639,sensor-publisher-01,12.58,20.75,127.68,585.17,7.42,33.28,6.96,100,Excellent,False,0.373
2025-12-02T18:59:36.810238,sensor-publisher-01,12.68,21.93,115.77,740.79,13.14,29.61,7.38,30,Poor,False,0.845
2025-12-02T18:59:50.059843,sensor-publisher-01,20.34,17.11,150.82,494.31,21.94,53.78,7.18,100,Excellent,False,0.652
```

## Implementation Examples

### Fetching Latest Data
```typescript
import { fetchLatestSensorData } from '@/services/mqttService';

const loadData = async () => {
  const data = await fetchLatestSensorData();
  if (data) {
    console.log(`Temperature: ${data.temperature}°C`);
    console.log(`Health Status: ${data.healthStatus}`);
  }
};
```

### Displaying in Component
```tsx
import { useEffect, useState } from 'react';
import { MQTTSensorData, fetchLatestSensorData } from '@/services/mqttService';

export const SensorDisplay = () => {
  const [data, setData] = useState<MQTTSensorData | null>(null);

  useEffect(() => {
    const loadData = async () => {
      const sensorData = await fetchLatestSensorData();
      setData(sensorData);
    };

    loadData();
    const interval = setInterval(loadData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <p>Temperature: {data.temperature}°C</p>
      <p>Moisture: {data.moisture}%</p>
      <p>Health: {data.healthStatus}</p>
    </div>
  );
};
```

## Troubleshooting

### Issue: "No MQTT data available"
- **Cause**: CSV file has no data rows
- **Solution**: 
  1. Ensure publisher is running
  2. Ensure subscriber is running
  3. Wait 60+ seconds for first data point
  4. Check `data/mqtt_sensor_data.csv` exists

### Issue: API returns 404
- **Cause**: Backend endpoints not found
- **Solution**:
  1. Restart Flask backend: `python backend/app.py`
  2. Verify API running on `http://localhost:5000`
  3. Check MQTT API endpoints are added

### Issue: Frontend can't fetch data
- **Cause**: CORS issue or wrong API URL
- **Solution**:
  1. Verify backend running on port 5000
  2. Check CORS is enabled in Flask
  3. Set `VITE_API_URL` environment variable if needed

### Issue: MQTT connection timeout
- **Cause**: Mosquitto broker not running
- **Solution**:
  1. Start Mosquitto: `mosquitto -v`
  2. Verify port 1883 is listening
  3. Check firewall allows port 1883

## Advanced Features

### Real-time Streaming (Future)
WebSocket endpoint for real-time updates:
```typescript
const cleanup = streamMQTTData(
  (data) => {
    // Handle new data
    setSensorData(data);
  },
  (error) => {
    // Handle error
    console.error(error);
  }
);
```

### Data Visualization
Integrate with charting libraries to visualize trends:
```typescript
import { LineChart } from 'recharts';

const data = await fetchSensorDataByTime(120); // Last 2 hours
<LineChart data={data}>
  <Line type="monotone" dataKey="temperature" stroke="#8884d8" />
</LineChart>
```

### Historical Analysis
Fetch and analyze historical patterns:
```typescript
const allData = await fetchAllSensorData();
const avgTemperature = allData.reduce((sum, d) => sum + d.temperature, 0) / allData.length;
```

## Performance Considerations

1. **CSV File Size**: Monitor `data/mqtt_sensor_data.csv` size
   - Grows ~100 bytes per 60 seconds
   - Archive old data after 1 month (1.4 MB)

2. **API Load**: Implement caching for historical queries
   - Cache `/api/mqtt/all` for 5 minutes
   - Cache `/api/mqtt/data?minutes=X` for 2 minutes

3. **Frontend Updates**: Use polling intervals wisely
   - Real-time: 1-5 second interval
   - Dashboard: 30-60 second interval
   - Archive view: 5+ minute interval

## Summary

The MQTT integration provides:
- ✅ Real-time sensor data collection
- ✅ Persistent CSV storage
- ✅ Backend API access
- ✅ Frontend display components
- ✅ Health analysis and anomaly detection
- ✅ Easy data refresh and manual loading

All components are production-ready and can be extended further!
