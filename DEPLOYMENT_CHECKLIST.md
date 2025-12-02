# Soil Health Backend - Deployment Checklist

## Pre-Deployment Verification

### ✅ Development Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Model trained (`python setup.py`)
- [ ] API tests passing (`python test_api.py`)

### ✅ Backend Configuration
- [ ] `.env.example` reviewed
- [ ] `.env` file created with production values
- [ ] Model directory exists with trained models
- [ ] CSV data file verified
- [ ] Logging directory created

### ✅ Frontend Configuration
- [ ] `VITE_API_URL` environment variable set
- [ ] API endpoint URL matches backend server
- [ ] CORS settings verified
- [ ] Service file imported in components

### ✅ Data Validation
- [ ] CSV file has correct format (2,880 records)
- [ ] All 7 parameters present
- [ ] Date range covers 1 month
- [ ] No missing values in data

### ✅ Model Validation
- [ ] Models successfully trained
- [ ] `models/health_model.pkl` exists
- [ ] `models/anomaly_model.pkl` exists
- [ ] `models/scaler.pkl` exists
- [ ] Test predictions working correctly

## Deployment Steps

### Step 1: Backend Preparation
```bash
# Clean up development files
rm -rf __pycache__
rm -rf .pytest_cache

# Verify production dependencies
pip install -r requirements.txt

# Run final tests
python test_api.py
```

### Step 2: Environment Configuration
Create production `.env` file:
```bash
cp .env.example .env
# Edit .env with production values
```

### Step 3: Server Deployment

#### Option A: Direct Python
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --access-logfile - app:app
```

#### Option B: Docker
```bash
# Build image
docker build -f Dockerfile -t soil-health-api:latest .

# Run container
docker run -d -p 5000:5000 \
  -e FLASK_ENV=production \
  -v $(pwd)/models:/app/models \
  --name soil-health-api \
  soil-health-api:latest
```

#### Option C: Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f soil-health-api
```

### Step 4: Verification

#### Check API Health
```bash
curl http://your-server:5000/health
```

#### Test Endpoints
```bash
python test_api.py
# All tests should pass
```

#### Check Logs
```bash
# Local
tail -f logs/app.log

# Docker
docker logs soil-health-api
```

### Step 5: Frontend Integration

#### Update API URL
In production frontend `.env.production`:
```
VITE_API_URL=https://api.yourdomain.com/api
```

#### Build Frontend
```bash
npm run build
```

#### Deploy Frontend
```bash
# Deploy build/ directory to your hosting
# Configure CORS origins in backend config
```

## Post-Deployment Verification

### ✅ API Connectivity
```bash
# Test from frontend server
curl -X POST http://your-api-server:5000/api/soil-health/health-index \
  -H "Content-Type: application/json" \
  -d '{"N": 22, "P": 18, "K": 150, "CO2": 500, "Temperature": 22, "Moisture": 55, "pH": 7.2}'
```

### ✅ Performance Monitoring
- [ ] Response time < 50ms
- [ ] Error rate < 1%
- [ ] CPU usage < 80%
- [ ] Memory usage < 500MB

### ✅ Error Handling
- [ ] Invalid requests return proper errors
- [ ] Server handles model load failures
- [ ] Database connection errors handled
- [ ] Timeout handling working

### ✅ Monitoring & Logging
- [ ] Logs being written to files
- [ ] Log rotation configured
- [ ] Health checks passing
- [ ] Metrics collection active

## Security Checklist

### ✅ Input Validation
- [ ] All inputs validated
- [ ] SQL injection prevention (if using DB)
- [ ] XSS protection enabled
- [ ] CORS properly configured

### ✅ Authentication (if applicable)
- [ ] API key validation working
- [ ] JWT tokens verified
- [ ] Rate limiting active
- [ ] Unauthorized requests blocked

### ✅ Data Security
- [ ] HTTPS enforced (production)
- [ ] Sensitive data not logged
- [ ] Model files protected
- [ ] Training data access restricted

### ✅ Network Security
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates valid
- [ ] VPN access (if needed)
- [ ] IP whitelist configured

## Production Configuration

### ✅ Environment Variables
```
FLASK_ENV=production
FLASK_DEBUG=0
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### ✅ Server Configuration
- [ ] Process manager (systemd/supervisord)
- [ ] Auto-restart on failure
- [ ] Resource limits set
- [ ] Health checks configured

### ✅ Database (if using)
- [ ] Connection pooling configured
- [ ] Backup strategy implemented
- [ ] Replication configured
- [ ] Performance indexes created

### ✅ Monitoring
- [ ] Application monitoring active
- [ ] Error tracking enabled
- [ ] Performance metrics collected
- [ ] Alerting configured

## Rollback Plan

### Rollback Steps
1. Stop new API server
2. Deploy previous version
3. Update frontend VITE_API_URL if needed
4. Verify all tests pass
5. Monitor error rates
6. Document what went wrong

### Backup & Recovery
- [ ] Database backup taken
- [ ] Model files backed up
- [ ] Configuration backed up
- [ ] Recovery procedure documented

## Performance Optimization

### ✅ Model Optimization
- [ ] Model compression considered
- [ ] Inference caching implemented
- [ ] Batch processing available
- [ ] Load testing completed

### ✅ API Optimization
- [ ] Response caching enabled
- [ ] Connection pooling used
- [ ] Compression enabled (gzip)
- [ ] Database queries optimized

### ✅ Deployment Optimization
- [ ] Worker processes tuned
- [ ] Memory limits optimized
- [ ] CPU allocation tested
- [ ] Network bandwidth checked

## Monitoring & Maintenance

### ✅ Daily Checks
- [ ] API health endpoint responding
- [ ] Error rates within threshold
- [ ] Response times acceptable
- [ ] Server resources available

### ✅ Weekly Tasks
- [ ] Review error logs
- [ ] Check performance metrics
- [ ] Test backup restoration
- [ ] Update documentation

### ✅ Monthly Tasks
- [ ] Analyze performance trends
- [ ] Review security logs
- [ ] Plan capacity upgrades
- [ ] Update dependencies

## Emergency Procedures

### API Down
1. Check server status: `systemctl status soil-health-api`
2. Check logs: `tail -f logs/app.log`
3. Restart service: `systemctl restart soil-health-api`
4. If models missing, retrain: `python setup.py`

### High Error Rate
1. Check recent deployments
2. Verify CSV data integrity
3. Test model predictions
4. Check server resources
5. Rollback if necessary

### High Latency
1. Check system load
2. Monitor database queries
3. Check network bandwidth
4. Scale horizontally or vertically
5. Implement caching

## Sign-Off

| Role | Name | Date | Sign-Off |
|------|------|------|----------|
| Backend Dev | | | ☐ |
| Frontend Dev | | | ☐ |
| DevOps | | | ☐ |
| QA | | | ☐ |
| Product Owner | | | ☐ |

## Post-Deployment Notes

**Deployment Date**: ___________
**Environment**: ___________
**Version**: ___________
**Issues**: ___________
**Performance**: ___________
**Next Steps**: ___________

---

**Deployment Status**: Ready for Production ✅
