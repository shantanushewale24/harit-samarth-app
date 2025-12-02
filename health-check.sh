#!/bin/bash
# Quick System Health Check

echo "==========================================="
echo "  Harit Samarth - System Health Check"
echo "==========================================="
echo ""

# Check Backend
echo "1. Backend API Check"
echo "   URL: http://127.0.0.1:5000/health"
response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/health 2>/dev/null || echo "000")
if [ "$response" = "200" ]; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend not responding (Code: $response)"
fi
echo ""

# Check Frontend
echo "2. Frontend Server Check"
echo "   URL: http://localhost:8080"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null || echo "000")
if [ "$response" = "200" ]; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend not responding (Code: $response)"
fi
echo ""

# Check Database
echo "3. Database Check"
if [ -f "backend/soil_health.db" ]; then
    count=$(sqlite3 backend/soil_health.db "SELECT COUNT(*) FROM sensor_readings;" 2>/dev/null || echo "0")
    echo "   ✅ Database exists with $count readings"
else
    echo "   ❌ Database file not found"
fi
echo ""

# Check API Endpoints
echo "4. API Endpoints Check"
echo "   Testing /api/soil-health/latest"
response=$(curl -s http://127.0.0.1:5000/api/soil-health/latest 2>/dev/null)
if echo "$response" | grep -q "soil_health_index"; then
    echo "   ✅ Latest reading endpoint working"
else
    echo "   ❌ Latest reading endpoint not working"
fi
echo ""

echo "==========================================="
echo "  Health Check Complete"
echo "==========================================="
