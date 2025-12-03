# Harit Samarth Network Setup - Quick Reference

## 🚀 Quick Start (60 seconds)

### For Publisher Device (Server):
```powershell
# Windows PowerShell
python network_setup.py
# Select option 1, enter your device IP
# Run the generated start_publisher.ps1
```

### For Receiver Device (Client):
```bash
# Any device on same network
python network_setup.py
# Select option 2, enter Publisher IP (e.g., 192.168.1.100)
npm install && npm run dev
```

---

## 🔧 Manual Configuration

### Find Your IP Address

**Windows:**
```powershell
ipconfig
# Look for IPv4 Address under your network adapter
# Example: 192.168.1.100
```

**Linux/Mac:**
```bash
ifconfig
# Or: hostname -I
```

---

## 📡 Environment Variables

### Publisher Device
```powershell
# Windows PowerShell
$env:MQTT_BROKER="192.168.1.100"
$env:MQTT_PORT="1883"
$env:BACKEND_API_URL="http://192.168.1.100:5000"

# Linux/Mac Bash
export MQTT_BROKER="192.168.1.100"
export MQTT_PORT="1883"
export BACKEND_API_URL="http://192.168.1.100:5000"
```

### Receiver Device (Frontend)
Create `.env.local` in project root:
```
VITE_BACKEND_API_URL=http://192.168.1.100:5000
```

Or create in `hardware module/smart-garden-hub/.env.local`:
```
VITE_BACKEND_API_URL=http://192.168.1.100:5000
```

---

## ✅ Verification Checklist

- [ ] Both devices on same network (ping test: `ping 192.168.1.100`)
- [ ] Publisher IP configured in environment variables
- [ ] Receiver `.env.local` created with Publisher IP
- [ ] Firewall allows ports: 5000 (API), 1883 (MQTT), 3306 (Database)
- [ ] MQTT Broker running (`mosquitto -v`)
- [ ] Backend API running (`python app.py`) - Check: `curl http://192.168.1.100:5000/`
- [ ] Sensor generator running (`python sensor_generator.py`)
- [ ] MQTT subscriber running (`python mqtt_sensor_subscriber.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] API returns data: `curl http://192.168.1.100:5000/api/soil-health/latest`
- [ ] Frontend shows real-time data and countdown timer

---

## 🔥 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Connection refused | Check firewall allows port 5000, 1883, 3306 |
| Cannot find device IP | Run `ipconfig` (Windows) or `ifconfig` (Linux) |
| .env.local not loaded | Restart dev server: `Ctrl+C` then `npm run dev` |
| MQTT broker not found | Ensure Mosquitto running: `mosquitto -v` or `docker run eclipse-mosquitto` |
| API returns 404 | Check BACKEND_API_URL format: `http://192.168.1.100:5000` (not https) |
| Timer shows N/A | Check frontend console for fetch errors, verify API URL |
| Data shows "Loading..." forever | API not responding - test: `curl http://192.168.1.100:5000/api/soil-health/latest` |

---

## 📚 Detailed Documentation

For complete setup instructions with diagrams and troubleshooting:
- **Full Guide**: `NETWORK_DEPLOYMENT_GUIDE.md`
- **Config Reference**: `NETWORK_CONFIG.py`
- **This Quick Start**: `NETWORK_SETUP_QUICK_REFERENCE.md`

---

## 🎯 Default Ports

| Service | Port | Device |
|---------|------|--------|
| Flask API | 5000 | Publisher |
| MQTT Broker | 1883 | Publisher |
| MySQL Database | 3306 | Publisher |
| Frontend Dev | 5173 (Vite) or 3000 | Receiver |

---

## 💡 Pro Tips

1. **Keep Publisher running**: Run all backend services on Publisher device continuously
2. **Multiple receivers**: Can connect many frontend devices to single Publisher
3. **Offline mode**: If you lose network, revert to `localhost` in `.env.local`
4. **Docker MQTT**: More reliable than Mosquitto: `docker run -d -p 1883:1883 eclipse-mosquitto`
5. **Test API first**: Always verify API responds before troubleshooting frontend

---

## 🔐 Security Notes (Production)

- Add MQTT authentication: Configure username/password in Mosquitto
- Use HTTPS: Put Flask behind nginx with SSL certificate
- API Authentication: Add token/API key validation
- Network segmentation: Only open ports to trusted devices
- See NETWORK_DEPLOYMENT_GUIDE.md for security best practices

---

Generated: 2024
For support: Check logs in backend output
