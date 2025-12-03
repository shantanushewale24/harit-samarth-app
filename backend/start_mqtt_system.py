#!/usr/bin/env python3
"""
MQTT Complete System Starter
Runs all components of the MQTT-integrated Harit Samarth system
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class SystemStarter:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend"
        
    def check_mqtt_broker(self):
        """Check if MQTT broker is running"""
        print("\n" + "="*60)
        print("🔍 Checking MQTT Broker...")
        print("="*60)
        
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 1883))
            sock.close()
            
            if result == 0:
                print("✓ MQTT Broker is running on localhost:1883")
                return True
            else:
                print("✗ MQTT Broker is NOT running on localhost:1883")
                print("\nTo start MQTT broker:")
                print("  Option 1 (Mosquitto): mosquitto -v")
                print("  Option 2 (Docker): docker run -d -p 1883:1883 eclipse-mosquitto")
                print("  Option 3 (Online): Use broker.hivemq.com (update MQTT_BROKER in code)")
                return False
        except Exception as e:
            print(f"✗ Error checking broker: {e}")
            return False
    
    def check_mysql(self):
        """Check if MySQL is running"""
        print("\n" + "="*60)
        print("🔍 Checking MySQL Database...")
        print("="*60)
        
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',
                port=3306
            )
            conn.close()
            print("✓ MySQL is running on localhost:3306")
            return True
        except Exception as e:
            print(f"✗ MySQL is NOT running")
            print("  Error: " + str(e))
            print("\nTo start MySQL:")
            print("  Windows: net start MySQL80")
            print("  Mac: brew services start mysql")
            print("  Linux: sudo systemctl start mysql")
            return False
    
    def start_component(self, name, script_path, cwd=None):
        """Start a Python component in background"""
        print(f"\n📍 Starting {name}...")
        try:
            cwd = cwd or self.backend_dir
            proc = subprocess.Popen(
                [sys.executable, script_path],
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            self.processes.append((name, proc))
            print(f"✓ {name} started (PID: {proc.pid})")
            return True
        except Exception as e:
            print(f"✗ Failed to start {name}: {e}")
            return False
    
    def run_system(self):
        """Run complete system"""
        print("\n" + "="*80)
        print("🚀 HARIT SAMARTH - MQTT INTEGRATED SYSTEM STARTER")
        print("="*80)
        
        # Pre-flight checks
        if not self.check_mqtt_broker():
            print("\n⚠️  MQTT Broker not available. System will work but in fallback mode.")
            response = input("Continue anyway? (y/n): ").lower()
            if response != 'y':
                print("❌ Aborted")
                return
        
        if not self.check_mysql():
            print("\n❌ MySQL is required. Please start MySQL and try again.")
            return
        
        # Start components
        print("\n" + "="*80)
        print("🔧 Starting Components...")
        print("="*80)
        
        components = [
            ("MQTT Sensor Subscriber", "mqtt_sensor_subscriber.py", self.backend_dir),
            ("Sensor Publisher (MQTT/API)", "mqtt_sensor_publisher.py", self.backend_dir),
            ("Flask API Backend", "app.py", self.backend_dir),
        ]
        
        for name, script, cwd in components:
            self.start_component(name, script, cwd)
            time.sleep(2)  # Wait between starts
        
        # Display system status
        print("\n" + "="*80)
        print("✅ SYSTEM RUNNING")
        print("="*80)
        print("\n📋 Running Components:")
        for name, proc in self.processes:
            status = "🟢 Running" if proc.poll() is None else "🔴 Stopped"
            print(f"  {status} - {name} (PID: {proc.pid})")
        
        print("\n📊 Access Points:")
        print("  🌐 Frontend: http://localhost:8080")
        print("  📡 API: http://localhost:5000")
        print("  🔌 MQTT Broker: localhost:1883")
        
        print("\n📋 Next Steps:")
        print("  1. Start frontend: npm run dev (in project root)")
        print("  2. Open browser: http://localhost:8080/hardware")
        print("  3. View sensor data on dashboard")
        
        print("\n💡 Monitoring Commands:")
        print("  # Watch MQTT messages:")
        print("  mosquitto_sub -h localhost -p 1883 -t 'harit-samarth/#' -v")
        print("  # Check database:")
        print("  mysql -u root -p soil_health_db -e 'SELECT COUNT(*) FROM sensor_readings;'")
        print("  # View API health:")
        print("  curl http://localhost:5000/health")
        
        print("\n" + "="*80)
        print("Press Ctrl+C to stop all components...")
        print("="*80 + "\n")
        
        # Keep running and monitor processes
        try:
            while True:
                # Check if any process has died
                all_running = True
                for name, proc in self.processes:
                    if proc.poll() is not None:
                        print(f"⚠️  {name} has stopped")
                        all_running = False
                
                time.sleep(5)
        
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        """Stop all running processes"""
        print("\n\n" + "="*80)
        print("🛑 Shutting Down...")
        print("="*80)
        
        for name, proc in reversed(self.processes):
            try:
                if proc.poll() is None:  # Process still running
                    print(f"  Stopping {name}...")
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    print(f"  ✓ {name} stopped")
            except Exception as e:
                print(f"  ✗ Error stopping {name}: {e}")
        
        print("\n✅ System shutdown complete\n")

def main():
    """Main entry point"""
    starter = SystemStarter()
    
    try:
        starter.run_system()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        starter.stop_all()

if __name__ == '__main__':
    main()
