# Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Git

## 5-Minute Setup

### Step 1: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup and training
python setup.py
```

### Step 2: Start Backend Server
```bash
python app.py
```
Backend will be at: `http://localhost:5000`

### Step 3: Test API (in new terminal)
```bash
cd backend
python test_api.py
```

### Step 4: Configure Frontend
In project root `.env.local`:
```
VITE_API_URL=http://localhost:5000/api
```

### Step 5: Start Frontend
```bash
npm install
npm run dev
```

## API Endpoints Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/soil-health/analyze` | Complete soil analysis |
| POST | `/api/soil-health/health-index` | Get health score only |
| POST | `/api/soil-health/anomaly` | Detect anomalies |
| POST | `/api/soil-health/critical-factors` | Identify problem areas |
| GET | `/api/soil-health/optimal-ranges` | Get reference ranges |
| POST | `/api/soil-health/batch-analyze` | Analyze multiple readings |

## Sample Requests

### Analyze Single Reading
```bash
curl -X POST http://localhost:5000/api/soil-health/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "N": 22,
    "P": 18,
    "K": 150,
    "CO2": 500,
    "Temperature": 22,
    "Moisture": 55,
    "pH": 7.2
  }'
```

### Get Health Index
```bash
curl -X POST http://localhost:5000/api/soil-health/health-index \
  -H "Content-Type: application/json" \
  -d '{
    "N": 22,
    "P": 18,
    "K": 150,
    "CO2": 500,
    "Temperature": 22,
    "Moisture": 55,
    "pH": 7.2
  }'
```

## Troubleshooting

**Q: "ModuleNotFoundError: No module named 'flask'"**
A: Run `pip install -r requirements.txt`

**Q: "Connection refused" from frontend**
A: Make sure backend is running: `python app.py`

**Q: CORS errors**
A: Flask-CORS is enabled. Check VITE_API_URL env var.

**Q: Models not found**
A: Run `python setup.py` to train models first.

## Health Index Interpretation

- **75-100**: Excellent - Soil is in optimal condition
- **60-74**: Good - Monitor key parameters
- **45-59**: Fair - Review critical factors
- **30-44**: Poor - Needs intervention
- **1-29**: Critical - Take immediate action

## File Locations

```
backend/
├── app.py                    # API server (run this)
├── soil_health_ml.py         # ML engine
├── setup.py                  # Setup script
├── test_api.py              # API tests
├── data/data.csv            # Training data
└── models/                  # (Auto-generated) Trained models
```

## Support

For detailed documentation, see `backend/README.md`
