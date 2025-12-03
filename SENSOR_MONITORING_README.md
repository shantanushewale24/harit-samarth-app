# 🌾 Sensor Monitoring Dashboard Implementation

## Overview

I've successfully implemented a complete **data persistence and real-time sensor monitoring system** for your Harit Samarth agricultural IoT platform. The system now keeps all sensor data in MySQL and CSV, displays live monitoring charts on the Hardware page, and provides data export capabilities.

---

## ✨ What's New

### 1. **Data Persistence (Fixed!)**
- ✅ **Historical Data Loading**: Sensor generator now loads last reading from database on startup instead of resetting to defaults
- ✅ **Dual-Write System**: Data saved to both MySQL and CSV simultaneously
- ✅ **Graceful Fallback**: If MySQL unavailable, falls back to CSV-only mode automatically
- ✅ **No More Data Loss**: Server restart preserves all historical data

### 2. **Real-Time Monitoring Dashboard**
- 📊 **NPK Nutrients Chart**: Line chart showing Nitrogen, Phosphorus, Potassium trends
- 🌡️ **Environmental Conditions**: Area chart for Temperature, Moisture, and CO2
- 📈 **Soil Health Metrics**: Bar chart for pH level and Health Index
- 🔔 **Anomaly Detection**: Visual alerts when sensor readings go out of normal range
- 📋 **Recent Readings Table**: Last 10 sensor measurements in detailed table format
- 🎯 **Health Status Badge**: Color-coded health indicators (Excellent/Good/Fair/Poor/Critical)
- 📊 **Data Statistics**: Summary showing total readings, average health, anomalies, etc.

### 3. **Export Functionality**
- 💾 **CSV Export**: Download all sensor readings as comma-separated values
- 📄 **JSON Export**: Download all readings in JSON format for analysis
- ⚡ **Real-time**: Export latest data with one click

### 4. **API Endpoints (All Working!)**

#### Sensor Analysis & Storage
```
POST /api/soil-health/analyze
  - Input: Sensor readings (N, P, K, CO2, Temperature, Moisture, pH)
  - Output: Health index, status, anomaly detection
  - Side effect: Saves to MySQL + CSV
```

#### Data Retrieval
```
GET /api/soil-health/latest
  - Returns: Last sensor reading with analysis
  - Used by: Sensor generator on startup for data continuity

GET /api/soil-health/history?limit=100
  - Returns: Last N readings (default 100)
  - Used by: Dashboard for chart visualization

GET /api/soil-health/stats
  - Returns: Summary statistics
  - Shows: Total readings, avg health, anomaly count, status distribution
```

#### Crop Recommendations
```
POST /api/crops/recommendations
  - Input: City/Location
  - Output: Top 3 recommended crops with suitability scores

GET /api/crops/details/<slug>
  - Returns: Detailed crop profile with management practices
```

---

## 🏗️ Architecture

### Backend (Flask + MySQL)
```
backend/
├── app.py (Main Flask server)
│   ├── Database initialization & schema
│   ├── Sensor data analysis functions
│   ├── API endpoints for soil health & crops
│   ├── Dual-write to MySQL + CSV
│   └── Graceful fallback logic
│
├── sensor_generator.py (Background sensor simulator)
│   ├── Loads historical data on startup ← NEW!
│   ├── Generates realistic sensor readings
│   ├── Posts data to API every 60 seconds
│   └── Handles API connection errors gracefully
│
├── models/
│   ├── crop_recommender.pkl (ML model)
│   └── crop_recommender_metrics.json
│
└── data/
    ├── sensor_readings.csv (CSV backup)
    └── crop_recommendations.csv (Training data)
```

### Frontend (React + Vite)
```
src/
├── pages/
│   └── Hardware.tsx ← Updated!
│       └── Now displays SensorMonitoring component
│
└── components/
    └── SensorMonitoring.tsx ← NEW! Complete dashboard
        ├── Fetches data from API every 10 seconds
        ├── Displays 4 chart types
        ├── Shows latest reading details
        ├── Export to CSV/JSON
        └── Real-time data statistics
```

### Database (MySQL)
```
soil_health_db
├── sensor_readings (main table)
│   ├── id (PRIMARY KEY)
│   ├── timestamp (indexed for fast queries)
│   ├── N, P, K, CO2 (nutrient & gas levels)
│   ├── temperature, moisture, pH (environmental)
│   ├── health_index (1-100 score)
│   ├── health_status (Excellent/Good/Fair/Poor/Critical)
│   ├── is_anomalous (boolean flag)
│   ├── anomaly_score (0-1 severity)
│   └── critical_factors (JSON array)
│
└── analysis_history (for tracking changes over time)
```

---

## 🚀 How to Use

### Start the System

1. **Terminal 1 - Backend Server**
```bash
cd backend
python app.py
```
Expected output:
```
✅ MySQL Database initialized successfully
✓ Loaded historical data from API
✓ Reading #1
  Time: 2025-12-02 17:44:48
  Health Index: 61/100 (Good)
  Anomaly: True (Score: 0.071)
  Critical Factors: Temperature, Moisture
  Next reading at: 17:45:48
```

2. **Terminal 2 - Frontend Dev Server**
```bash
npm run dev
```
Server runs on http://localhost:8080

### Access the Dashboard

1. Open browser: **http://localhost:8080/hardware**
2. You'll see:
   - Latest sensor reading with color-coded health status
   - 4 interactive charts updating in real-time
   - Recent readings table
   - Export buttons for CSV/JSON
   - Data statistics summary

### Export Data

- **CSV Export**: Click "Download CSV" button
  - Includes: timestamp, all sensor readings, health analysis, anomaly data
  - Filename: `sensor-readings-{timestamp}.csv`
  
- **JSON Export**: Click "Download JSON" button
  - Full data structure for data analysis tools
  - Filename: `sensor-readings-{timestamp}.json`

---

## 🔄 Data Flow

```
Hardware Sensors
       ↓
Sensor Generator (backend/sensor_generator.py)
       ↓
      POST /api/soil-health/analyze
       ↓
Flask Backend (app.py)
       ├→ Analyze: Calculate health index, detect anomalies
       ├→ Save to MySQL (soil_health_db.sensor_readings)
       └→ Save to CSV (data/sensor_readings.csv)
       ↓
      Response with analysis results
       ↓
Frontend SensorMonitoring Component
       ├→ GET /api/soil-health/latest (for latest card)
       ├→ GET /api/soil-health/history (for charts)
       └→ Polls every 10 seconds for updates
       ↓
User Dashboard
       ├→ Interactive Charts
       ├→ Real-time Alerts
       ├→ Data Export
       └→ Statistics
```

---

## 📊 Key Features Explained

### Health Index Calculation
Soil health is scored 1-100 based on:
- **Nitrogen (N)**: Optimal 15-30 ppm - Essential for plant growth
- **Phosphorus (P)**: Optimal 10-25 ppm - Root development & energy
- **Potassium (K)**: Optimal 100-200 ppm - Overall plant vigor
- **CO2**: Optimal 400-600 ppm - Photosynthesis efficiency
- **Temperature**: Optimal 15-25°C - Microbial activity
- **Moisture**: Optimal 40-60% - Water availability
- **pH**: Optimal 6.5-7.5 - Nutrient solubility

**Status Thresholds:**
- 75-100: **Excellent** 🟢 (Ideal conditions)
- 60-74: **Good** 🔵 (Satisfactory, minor adjustments)
- 45-59: **Fair** 🟡 (Moderate issues, intervention needed)
- 30-44: **Poor** 🟠 (Significant problems)
- 1-29: **Critical** 🔴 (Immediate action required)

### Anomaly Detection
- Monitors 7 key parameters against expected ranges
- Flags anomalies when values deviate significantly
- Calculates anomaly severity score (0-1)
- Shows critical factors affecting soil health
- Visual alert badge on dashboard

---

## 🔧 Configuration

### Sensor Generator (backend/sensor_generator.py)
```python
UPDATE_INTERVAL = 60  # Generate reading every 60 seconds
BASE_READINGS = {     # Default values (used if no history)
    'N': 22,
    'P': 18,
    'K': 150,
    'CO2': 500,
    'Temperature': 22,
    'Moisture': 55,
    'pH': 7.2
}
```

### Dashboard Updates (src/components/SensorMonitoring.tsx)
```typescript
const interval = setInterval(fetchData, 10000);  // Poll every 10 seconds
const limit = 100;  // Show last 100 readings
```

### MySQL Connection (backend/app.py)
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',  # Update if different
    'port': 3306,
    'database': 'soil_health_db'
}
```

---

## 📈 Testing & Verification

### 1. Check Backend Status
```bash
# Test API health
curl http://localhost:5000/health

# Get latest reading
curl http://localhost:5000/api/soil-health/latest

# Get statistics
curl http://localhost:5000/api/soil-health/stats

# Get history (limit to 5)
curl "http://localhost:5000/api/soil-health/history?limit=5"
```

### 2. Verify Data Persistence
```bash
# Open MySQL client
mysql -u root -p

# Check sensor readings
SELECT COUNT(*) FROM soil_health_db.sensor_readings;
SELECT * FROM soil_health_db.sensor_readings ORDER BY timestamp DESC LIMIT 5;

# Check health status distribution
SELECT health_status, COUNT(*) FROM soil_health_db.sensor_readings GROUP BY health_status;
```

### 3. Test Data Persistence After Restart
1. Note current data count: `SELECT COUNT(*) FROM sensor_readings;`
2. Restart backend: Kill process and run `python app.py` again
3. Generate 1-2 new readings (wait 60 seconds)
4. Check data count again - should be higher!

---

## 🎨 Dashboard Sections

### 1. **Header** 
- Title: "🌾 Soil Health Monitor"
- Refresh button for manual updates

### 2. **Latest Reading Card**
- Health status badge (color-coded)
- Last reading timestamp
- Key metrics in 4-column grid:
  - Health Index %
  - Temperature °C
  - Moisture %
  - pH Level
- Anomaly indicator with severity score

### 3. **NPK Nutrients Chart**
- Line chart showing Nitrogen, Phosphorus, Potassium
- X-axis: Time (HH:MM:SS)
- Y-axis: PPM concentration
- Color-coded lines for each nutrient

### 4. **Environmental Conditions Chart**
- Area chart for Temperature, Moisture, CO2
- Stacked area visualization
- Shows trends over time

### 5. **Soil Health Metrics Chart**
- Bar chart with pH and Health Index
- Side-by-side comparison
- Helps identify pH impact on health

### 6. **Recent Readings Table**
- Last 10 sensor measurements
- 8 columns: Time, N, P, K, Temp, Moisture, pH, Health
- Hover effect for interactivity
- Scrollable on small screens

### 7. **Export Section**
- CSV button: Download with full headers
- JSON button: Download for data analysis
- Shows record count being exported

### 8. **Data Summary**
- Total readings count
- Average health index
- Number of anomalies detected
- Anomaly percentage

---

## 🐛 Troubleshooting

### Issue: "No data available" on dashboard
**Solution:**
1. Ensure backend is running: `curl http://localhost:5000/health`
2. Wait 60 seconds for first sensor reading to be generated
3. Check MySQL is running: `mysql -u root -p -e "SELECT 1;"`

### Issue: Backend won't start
**Check:**
```bash
# Is MySQL running?
mysql -u root -p -e "SELECT @@version;"

# Is port 5000 available?
netstat -tuln | grep 5000

# Check dependencies
pip install -r requirements.txt
```

### Issue: Data not saving to database
**Debug:**
```bash
# Check MySQL connection
python -c "import mysql.connector; mysql.connector.connect(user='root', password='password', host='localhost', database='soil_health_db')"

# Check CSV fallback is working
ls -la data/sensor_readings.csv
tail -20 data/sensor_readings.csv
```

### Issue: Charts not updating
**Solution:**
1. Check browser console for errors (F12)
2. Verify frontend can reach backend:
   ```bash
   curl http://localhost:5000/api/soil-health/history?limit=1
   ```
3. Check CORS headers if on different domain

---

## 🔐 Production Considerations

### Before Going Live:

1. **Security**
   - Add authentication to API endpoints
   - Use HTTPS instead of HTTP
   - Add request validation and sanitization
   - Implement rate limiting

2. **Performance**
   - Use connection pooling for MySQL
   - Add caching for history queries
   - Implement pagination for large datasets
   - Consider time-series DB (InfluxDB) for high-frequency data

3. **Reliability**
   - Set up database backups
   - Add monitoring and alerting
   - Implement circuit breakers for API calls
   - Use WSGI server (Gunicorn) instead of Flask dev server

4. **Scalability**
   - Migrate to production database
   - Use load balancer for multiple backend instances
   - Consider cloud deployment (AWS, Azure, GCP)
   - Archive old sensor data to time-series database

---

## 📝 Files Modified/Created

### Created:
- ✨ `src/components/SensorMonitoring.tsx` - Complete monitoring dashboard

### Modified:
- 🔄 `src/pages/Hardware.tsx` - Now uses SensorMonitoring component
- 🔄 `backend/sensor_generator.py` - Added _load_historical_data() method
- 🔄 `backend/app.py` - Already had all endpoints needed!

### Existing (Already Working):
- `backend/app.py` - API endpoints for history, latest, stats
- `backend/sensor_generator.py` - Sensor data generation
- MySQL database - Persistent storage

---

## 🎯 Next Steps (Optional Enhancements)

1. **Advanced Analytics**
   - Trend analysis with linear regression
   - Seasonal pattern detection
   - Predictive alerts ("Health will drop in 2 hours if...")

2. **Mobile App**
   - React Native port for iOS/Android
   - Push notifications for anomalies
   - Offline mode with data sync

3. **Integration**
   - WhatsApp/Telegram alerts
   - MQTT integration for real hardware sensors
   - Integration with agricultural advisors
   - Government subsidy tracking

4. **AI Features**
   - ML-based anomaly detection
   - Automatic crop recommendations based on trends
   - Soil type classification from readings
   - Climate resilience analysis

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review backend logs: `backend_debug.log`
3. Check browser console (F12 → Console tab)
4. Verify database: `mysql -u root -p soil_health_db`

---

## 🎉 Summary

Your Harit Samarth platform now has:
- ✅ Persistent sensor data storage (MySQL + CSV backup)
- ✅ Real-time monitoring dashboard with 4 chart types
- ✅ Automatic anomaly detection with visual alerts
- ✅ Data export to CSV and JSON formats
- ✅ Complete API for crop recommendations and soil analysis
- ✅ Graceful degradation (falls back to CSV if MySQL unavailable)
- ✅ Historical data continuity (no data loss on restart)

**The system is production-ready for testing and can be scaled for real sensor hardware!** 🌾📊
