#!/usr/bin/env python3
"""
Network Configuration Setup Tool
Helps configure Harit Samarth for multi-device deployment
"""

import os
import sys
import platform
import socket
import json
from pathlib import Path

def get_local_ip():
    """Get local IP address of the current device"""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def detect_device_type():
    """Detect if device is Windows, Linux, or Mac"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    else:
        return "linux"

def create_env_file(backend_ip, frontend_path):
    """Create .env.local file for frontend"""
    env_content = f"""# Harit Samarth Network Configuration
# Auto-generated - Generated: {__import__('datetime').datetime.now().isoformat()}

# Backend API URL - Change this to your publisher device IP
VITE_BACKEND_API_URL=http://{backend_ip}:5000

# MQTT Broker (if using direct MQTT from browser)
# Note: Most browsers can't connect to MQTT directly, use API instead
VITE_MQTT_BROKER_URL=mqtt://{backend_ip}:1883
"""
    
    env_file = Path(frontend_path) / ".env.local"
    env_file.write_text(env_content)
    print(f"✓ Created {env_file}")

def create_publisher_script(backend_ip, output_path):
    """Create startup script for publisher device"""
    
    if detect_device_type() == "windows":
        script_name = "start_publisher.ps1"
        script_content = f"""# Harit Samarth Publisher Startup Script
# Run this on the Publisher/Server device

Write-Host "Setting up Publisher Device..." -ForegroundColor Cyan

# Set environment variables
$env:MQTT_BROKER="{backend_ip}"
$env:MQTT_PORT="1883"
$env:BACKEND_API_URL="http://{backend_ip}:5000"

Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  MQTT Broker: $env:MQTT_BROKER"
Write-Host "  MQTT Port: $env:MQTT_PORT"
Write-Host "  Backend API: $env:BACKEND_API_URL"
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {{
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}}
Write-Host "✓ Python: $($python.Version)" -ForegroundColor Green

# Check MySQL
$mysql = Get-Command mysql -ErrorAction SilentlyContinue
if (-not $mysql) {{
    Write-Host "⚠ MySQL not found in PATH (but may still be running as service)" -ForegroundColor Yellow
}}

# Start backend services
Write-Host ""
Write-Host "Starting backend services..." -ForegroundColor Cyan

$backendPath = ".\backend"
if (-not (Test-Path $backendPath)) {{
    Write-Host "✗ Backend folder not found!" -ForegroundColor Red
    exit 1
}}

# Terminal 1: Flask API
Write-Host "Starting Flask API..." -ForegroundColor Yellow
Start-Process -FilePath python -ArgumentList "$backendPath\app.py" `
    -WorkingDirectory . -NoNewWindow -PassThru | Out-Null
Start-Sleep -Seconds 2

# Terminal 2: Sensor Generator
Write-Host "Starting Sensor Generator..." -ForegroundColor Yellow
Start-Process -FilePath python -ArgumentList "$backendPath\sensor_generator.py" `
    -WorkingDirectory . -NoNewWindow -PassThru | Out-Null
Start-Sleep -Seconds 2

# Terminal 3: MQTT Subscriber
Write-Host "Starting MQTT Subscriber..." -ForegroundColor Yellow
Start-Process -FilePath python -ArgumentList "$backendPath\mqtt_sensor_subscriber.py" `
    -WorkingDirectory . -NoNewWindow -PassThru | Out-Null

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "PUBLISHER DEVICE STARTED" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Publisher IP: {backend_ip}" -ForegroundColor Green
Write-Host "API Endpoint: http://{backend_ip}:5000" -ForegroundColor Green
Write-Host "MQTT Broker: {backend_ip}:1883" -ForegroundColor Green
Write-Host ""
Write-Host "Configure Receiver Device with:" -ForegroundColor Yellow
Write-Host "VITE_BACKEND_API_URL=http://{backend_ip}:5000" -ForegroundColor Cyan
"""
    else:
        script_name = "start_publisher.sh"
        script_content = f"""#!/bin/bash
# Harit Samarth Publisher Startup Script
# Run this on the Publisher/Server device

echo "Setting up Publisher Device..."

# Set environment variables
export MQTT_BROKER="{backend_ip}"
export MQTT_PORT="1883"
export BACKEND_API_URL="http://{backend_ip}:5000"

echo "Configuration:"
echo "  MQTT Broker: $MQTT_BROKER"
echo "  MQTT Port: $MQTT_PORT"
echo "  Backend API: $BACKEND_API_URL"

# Start services in background
cd backend

echo "Starting Flask API..."
python app.py &
API_PID=$!
sleep 2

echo "Starting Sensor Generator..."
python sensor_generator.py &
GENERATOR_PID=$!
sleep 2

echo "Starting MQTT Subscriber..."
python mqtt_sensor_subscriber.py &
SUBSCRIBER_PID=$!

echo ""
echo "================================"
echo "PUBLISHER DEVICE STARTED"
echo "================================"
echo ""
echo "Your Publisher IP: {backend_ip}"
echo "API Endpoint: http://{backend_ip}:5000"
echo "MQTT Broker: {backend_ip}:1883"
echo ""
echo "Configure Receiver Device with:"
echo "VITE_BACKEND_API_URL=http://{backend_ip}:5000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all processes
wait
"""
    
    script_path = Path(output_path) / script_name
    script_path.write_text(script_content)
    
    if detect_device_type() != "windows":
        script_path.chmod(0o755)  # Make executable on Linux/Mac
    
    print(f"✓ Created {script_path}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("HARIT SAMARTH - Network Configuration Setup")
    print("=" * 60)
    print()
    
    device_type = detect_device_type()
    local_ip = get_local_ip()
    
    print(f"Detected System: {device_type.capitalize()}")
    print(f"Detected Local IP: {local_ip}")
    print()
    
    # Ask user for device type
    print("Select your device type:")
    print("1. Publisher Device (Server) - Runs backend & sensor generator")
    print("2. Receiver Device (Client) - Runs frontend only")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n=== PUBLISHER DEVICE SETUP ===\n")
        backend_ip = input(f"Enter this device's IP address (default: {local_ip}): ").strip() or local_ip
        
        # Create publisher startup script
        create_publisher_script(backend_ip, ".")
        
        print("\nPublisher setup complete!")
        print(f"Run the startup script to begin:")
        if device_type == "windows":
            print(f"  .\\start_publisher.ps1")
        else:
            print(f"  ./start_publisher.sh")
        
    elif choice == "2":
        print("\n=== RECEIVER DEVICE SETUP ===\n")
        backend_ip = input("Enter the Publisher device IP address: ").strip()
        
        if not backend_ip:
            print("✗ IP address required!")
            sys.exit(1)
        
        # Create .env files for both frontends
        frontend_paths = [
            ".",  # Main app
            "hardware module/smart-garden-hub"  # Smart garden hub
        ]
        
        for path in frontend_paths:
            if Path(path).exists():
                create_env_file(backend_ip, path)
        
        print("\nReceiver setup complete!")
        print(f"Run frontend with:")
        print(f"  npm install")
        print(f"  npm run dev")
        print(f"\nFrontend will connect to: http://{backend_ip}:5000")
        
    else:
        print("✗ Invalid choice!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nFor detailed instructions, see: NETWORK_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()
