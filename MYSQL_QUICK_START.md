# MySQL Migration - Quick Start Guide

## 🎯 What Was Done

Your backend has been successfully migrated from SQLite to MySQL with **dual data storage**:
- ✅ All sensor data saved to MySQL database
- ✅ Backup copy saved to CSV files  
- ✅ All API endpoints updated
- ✅ Real-time sensor generator connected

## 🚀 Getting Started

### 1. Update MySQL Credentials
Edit `backend/app.py` lines 28-33:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD',  # ← Add your MySQL password here
    'database': 'soil_health_db',
    'port': 3306
}
```

### 2. Start MySQL Server
```bash
# Windows
net start MySQL80  # or your MySQL service name

# Or use MySQL client
mysql -u root -p
```

### 3. Start Backend
```bash
cd backend
python app.py
```

Expected output:
```
* Serving Flask app 'app'
* MySQL Database initialized successfully
* Sensor data generator started in background
* Running on http://0.0.0.0:5000
```

### 4. Verify Data Storage
Check CSV file:
```bash
# Should see data in:
backend/data/sensor_readings.csv
```

Query MySQL:
```sql
SELECT * FROM soil_health_db.sensor_readings LIMIT 5;
```

## 📊 Data Storage Comparison

| Feature | SQLite | CSV | MySQL |
|---------|--------|-----|-------|
| **Before** | Used only | N/A | N/A |
| **Now** | ❌ Removed | ✅ Backup | ✅ Primary |
| **Scalability** | Small | Medium | Large |
| **Queries** | Simple | Very Limited | Advanced |
| **Redundancy** | None | ✅ Yes | ✅ Yes |

## 🔄 Data Flow

```
Sensor Data (every 60 sec)
         ↓
Backend API /analyze endpoint
         ↓
  ML Analysis (health, anomalies)
    ↙          ↘
  CSV file      MySQL database
 (Backup)      (Primary storage)
         ↓
Frontend Dashboard (reads from MySQL)
```

## 📝 API Endpoints

All endpoints now use MySQL:

### Analyze & Store
```bash
POST /api/soil-health/analyze
{
  "N": 22,
  "P": 18,
  "K": 150,
  "CO2": 500,
  "Temperature": 22,
  "Moisture": 55,
  "pH": 7.2
}
```

### Get Latest
```bash
GET /api/soil-health/latest
# Returns: Latest reading from MySQL
```

### Get History
```bash
GET /api/soil-health/history?limit=100
# Returns: Last 100 readings from MySQL
```

### Get Statistics
```bash
GET /api/soil-health/stats
# Returns: Aggregated stats from MySQL
```

## ✅ Files Modified

- **app.py** - Complete SQLite → MySQL conversion
- **sensor_generator.py** - No changes (works with new API)
- **Frontend** - No changes (API compatible)

## ⚠️ Important Notes

1. **Old SQLite database** (`soil_health.db`) is still in `backend/` - can be deleted after verifying MySQL works

2. **CSV backup** is automatically created in `backend/data/sensor_readings.csv` - useful for:
   - Data backup
   - Offline analysis
   - Migration reference

3. **No data loss** - If MySQL goes down, CSV continues recording

4. **Schema creation** happens automatically on first run

## 🔧 Troubleshooting

### MySQL Connection Error
```python
# Error: "MySQL Connection Error"
# Solution: Check credentials in MYSQL_CONFIG
# Verify MySQL service is running
```

### "Database doesn't exist"
```
# Solution: Automatic - creates on first run
# If manual: CREATE DATABASE soil_health_db;
```

### "Table doesn't exist"
```
# Solution: Automatic - creates on first run
# Or restart backend: python app.py
```

### CSV not updating
```
# Check: backend/data/ directory exists
# If missing: Manually create backend/data/ folder
```

## 📈 Monitoring

Check system health:
```bash
# View latest MySQL data
curl http://localhost:5000/api/soil-health/latest

# View statistics
curl http://localhost:5000/api/soil-health/stats

# Health check
curl http://localhost:5000/health
```

## 🎓 Key Changes at a Glance

| Component | Before | After |
|-----------|--------|-------|
| **Database** | SQLite (.db) | MySQL + CSV |
| **Table Columns** | nitrogen, phosphorus... | N, P, K, CO2... |
| **Imports** | sqlite3 | mysql.connector |
| **Queries** | SQL with ? | SQL with %s |
| **Scalability** | Limited | Enterprise-ready |
| **Backup** | Manual | Automatic (CSV) |

## 📞 Support

For issues:
1. Check backend logs for error messages
2. Verify MySQL is running: `mysql -u root`
3. Confirm credentials match `MYSQL_CONFIG`
4. Check `backend/data/sensor_readings.csv` exists
5. Restart backend: `python app.py`

---

✅ **Status**: Migration Complete and Ready to Use
**Date**: 2024
**Next Step**: Update MYSQL_CONFIG password and start the backend
