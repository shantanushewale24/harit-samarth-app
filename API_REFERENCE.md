# Soil Health Backend - API Reference Guide

## Base URL
```
http://localhost:5000/api/soil-health
```

## Authentication
Currently no authentication required. Add API keys or JWT for production.

## Response Format
All responses are in JSON format with appropriate HTTP status codes.

---

## Endpoints

### 1. Analyze Soil Health
**Complete analysis including health index, anomalies, and critical factors**

```http
POST /api/soil-health/analyze
Content-Type: application/json
```

#### Request Body
```json
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

#### Response (200 OK)
```json
{
  "timestamp": "2024-11-01T12:30:00.123456",
  "soil_health_index": 78,
  "health_status": "Good",
  "is_anomalous": false,
  "anomaly_score": 0.15,
  "critical_factors": [],
  "sensor_reading": {
    "N": 22,
    "P": 18,
    "K": 150,
    "CO2": 500,
    "Temperature": 22,
    "Moisture": 55,
    "pH": 7.2
  }
}
```

#### Error Responses
```json
{
  "error": "Missing required fields",
  "required": ["N", "P", "K", "CO2", "Temperature", "Moisture", "pH"]
}
```

#### cURL Example
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

---

### 2. Get Health Index
**Get only the soil biological health score (1-100)**

```http
POST /api/soil-health/health-index
Content-Type: application/json
```

#### Request Body
```json
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

#### Response (200 OK)
```json
{
  "health_index": 78,
  "health_status": "Good",
  "scale": "1-100"
}
```

#### Status Reference
- **75-100**: Excellent
- **60-74**: Good
- **45-59**: Fair
- **30-44**: Poor
- **1-29**: Critical

---

### 3. Detect Anomalies
**Identify unusual sensor readings**

```http
POST /api/soil-health/anomaly
Content-Type: application/json
```

#### Request Body
```json
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

#### Response (200 OK)
```json
{
  "is_anomalous": false,
  "anomaly_score": 0.15,
  "severity": "Low"
}
```

#### Severity Reference
- **Low**: 0.0-0.33
- **Medium**: 0.34-0.66
- **High**: 0.67-1.0

#### Example - Anomalous Reading
```json
{
  "is_anomalous": true,
  "anomaly_score": 0.82,
  "severity": "High"
}
```

---

### 4. Get Critical Factors
**Identify parameters affecting soil health negatively**

```http
POST /api/soil-health/critical-factors
Content-Type: application/json
```

#### Request Body
```json
{
  "N": 8,
  "P": 22,
  "K": 180,
  "CO2": 450,
  "Temperature": 28,
  "Moisture": 72,
  "pH": 8.2
}
```

#### Response (200 OK)
```json
{
  "critical_factors": [
    "Nitrogen: 8 (Optimal: 15-30)",
    "Temperature: 28°C (Optimal: 15-25°C)",
    "Moisture: 72% (Optimal: 40-60%)"
  ],
  "factor_count": 3,
  "status": "Needs Attention"
}
```

#### Response (Healthy Soil)
```json
{
  "critical_factors": [],
  "factor_count": 0,
  "status": "Healthy"
}
```

---

### 5. Get Optimal Ranges
**Retrieve reference optimal ranges for all parameters**

```http
GET /api/soil-health/optimal-ranges
Content-Type: application/json
```

#### Response (200 OK)
```json
{
  "optimal_ranges": {
    "N": {
      "min": 15,
      "max": 30,
      "unit": "mg/kg",
      "description": "Nitrogen - Essential for plant growth"
    },
    "P": {
      "min": 10,
      "max": 25,
      "unit": "mg/kg",
      "description": "Phosphorus - Important for root development"
    },
    "K": {
      "min": 100,
      "max": 200,
      "unit": "mg/kg",
      "description": "Potassium - Vital for plant health"
    },
    "CO2": {
      "min": 400,
      "max": 600,
      "unit": "ppm",
      "description": "Carbon Dioxide - Affects soil respiration"
    },
    "Temperature": {
      "min": 15,
      "max": 25,
      "unit": "°C",
      "description": "Soil Temperature - Affects microbial activity"
    },
    "Moisture": {
      "min": 40,
      "max": 60,
      "unit": "%",
      "description": "Soil Moisture - Critical for nutrient availability"
    },
    "pH": {
      "min": 6.5,
      "max": 7.5,
      "unit": "pH",
      "description": "pH - Affects nutrient availability"
    }
  }
}
```

#### cURL Example
```bash
curl http://localhost:5000/api/soil-health/optimal-ranges
```

---

### 6. Batch Analyze
**Analyze multiple sensor readings in a single request**

```http
POST /api/soil-health/batch-analyze
Content-Type: application/json
```

#### Request Body
```json
{
  "readings": [
    {
      "N": 22,
      "P": 18,
      "K": 150,
      "CO2": 500,
      "Temperature": 22,
      "Moisture": 55,
      "pH": 7.2
    },
    {
      "N": 20,
      "P": 16,
      "K": 145,
      "CO2": 510,
      "Temperature": 21,
      "Moisture": 52,
      "pH": 7.1
    },
    {
      "N": 24,
      "P": 20,
      "K": 155,
      "CO2": 490,
      "Temperature": 23,
      "Moisture": 58,
      "pH": 7.3
    }
  ]
}
```

#### Response (200 OK)
```json
{
  "count": 3,
  "analyses": [
    {
      "timestamp": "2024-11-01T12:00:00.123456",
      "soil_health_index": 78,
      "health_status": "Good",
      "is_anomalous": false,
      "anomaly_score": 0.15,
      "critical_factors": [],
      "sensor_reading": {...}
    },
    {
      "timestamp": "2024-11-01T12:30:00.123456",
      "soil_health_index": 76,
      "health_status": "Good",
      "is_anomalous": false,
      "anomaly_score": 0.12,
      "critical_factors": [],
      "sensor_reading": {...}
    },
    {
      "timestamp": "2024-11-01T13:00:00.123456",
      "soil_health_index": 80,
      "health_status": "Good",
      "is_anomalous": false,
      "anomaly_score": 0.18,
      "critical_factors": [],
      "sensor_reading": {...}
    }
  ]
}
```

#### Maximum Batch Size
- Recommended: 100-1000 readings per batch
- Maximum tested: 1000+ readings
- For larger batches, split into multiple requests

#### cURL Example
```bash
curl -X POST http://localhost:5000/api/soil-health/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {"N": 22, "P": 18, "K": 150, "CO2": 500, "Temperature": 22, "Moisture": 55, "pH": 7.2},
      {"N": 20, "P": 16, "K": 145, "CO2": 510, "Temperature": 21, "Moisture": 52, "pH": 7.1}
    ]
  }'
```

---

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Analysis completed |
| 400 | Bad Request | Missing required fields |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Internal error |

---

## Error Handling

### Missing Fields
```json
{
  "error": "Missing required fields",
  "required": ["N", "P", "K", "CO2", "Temperature", "Moisture", "pH"]
}
```

### Invalid Data Type
```json
{
  "error": "Invalid data type: could not convert string to float"
}
```

### Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Parameter Units & Ranges

### Required Parameters

| Parameter | Unit | Critical Min | Optimal Min | Optimal Max | Critical Max |
|-----------|------|--------------|-------------|-------------|--------------|
| N | mg/kg | 5 | 15 | 30 | 40 |
| P | mg/kg | 2.5 | 10 | 25 | 35 |
| K | mg/kg | 25 | 100 | 200 | 300 |
| CO2 | ppm | 200 | 400 | 600 | 800 |
| Temperature | °C | 5 | 15 | 25 | 30 |
| Moisture | % | 20 | 40 | 60 | 70 |
| pH | pH | 5.5 | 6.5 | 7.5 | 8.5 |

---

## Integration Examples

### JavaScript/TypeScript
```typescript
const response = await fetch('http://localhost:5000/api/soil-health/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    N: 22, P: 18, K: 150, CO2: 500,
    Temperature: 22, Moisture: 55, pH: 7.2
  })
});
const data = await response.json();
console.log(data.soil_health_index);
```

### Python
```python
import requests

response = requests.post(
    'http://localhost:5000/api/soil-health/analyze',
    json={
        'N': 22, 'P': 18, 'K': 150, 'CO2': 500,
        'Temperature': 22, 'Moisture': 55, 'pH': 7.2
    }
)
print(response.json()['soil_health_index'])
```

### cURL
```bash
curl -X POST http://localhost:5000/api/soil-health/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "N": 22, "P": 18, "K": 150, "CO2": 500,
    "Temperature": 22, "Moisture": 55, "pH": 7.2
  }'
```

---

## Performance Tips

1. **Use Batch Analysis** for multiple readings (faster than individual calls)
2. **Cache Optimal Ranges** - Get once, use many times
3. **Implement Local Validation** before sending to API
4. **Use Connection Pooling** for multiple requests
5. **Monitor Response Times** and alert if > 100ms

---

## Troubleshooting

### "Connection refused"
- Ensure Flask server is running
- Check server port is correct (default: 5000)
- Verify firewall allows connections

### "Invalid data type"
- Ensure all numeric fields are numbers (not strings)
- Check for missing or null values
- Verify parameter names match exactly

### "Missing required fields"
- Include all 7 parameters
- Check spelling (case-sensitive)
- Verify parameter order doesn't matter

### Slow Response Times
- Check server load (CPU, memory)
- Monitor network latency
- Consider batch processing
- Check for model loading issues

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-11-01 | Initial release |

---

**Last Updated**: Dec 2, 2024
**Status**: Production Ready ✅
