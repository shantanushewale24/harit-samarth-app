#!/usr/bin/env python3
"""
MQTT Setup Tester
Verifies that MQTT components are properly installed and configured
"""

import subprocess
import sys
import importlib
import os


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_mosquitto():
    """Check if Mosquitto is installed"""
    print_section("1. Checking Mosquitto Installation")
    
    try:
        result = subprocess.run(["mosquitto", "-h"], capture_output=True, text=True, timeout=2)
        print("✅ Mosquitto is installed")
        return True
    except FileNotFoundError:
        print("❌ Mosquitto NOT found")
        print("\nTo install Mosquitto:")
        print("  Windows (Chocolatey): choco install mosquitto")
        print("  Windows (Manual):     Download from https://mosquitto.org/download/")
        print("  macOS:                brew install mosquitto")
        print("  Linux:                sudo apt-get install mosquitto")
        return False
    except Exception as e:
        print(f"⚠️  Error checking Mosquitto: {e}")
        return False


def check_paho_mqtt():
    """Check if paho-mqtt is installed"""
    print_section("2. Checking paho-mqtt Package")
    
    try:
        import paho.mqtt.client
        import paho.mqtt
        print("✅ paho-mqtt is installed")
        print(f"   Version: {paho.mqtt.__version__ if hasattr(paho.mqtt, '__version__') else 'unknown'}")
        return True
    except ImportError:
        print("❌ paho-mqtt NOT found")
        print("\nTo install paho-mqtt:")
        print("  Run: pip install paho-mqtt")
        return False


def check_mqtt_files():
    """Check if MQTT configuration files exist"""
    print_section("3. Checking MQTT Configuration Files")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(base_path, "backend")
    
    files_to_check = [
        ("mqtt_config.py", os.path.join(backend_path, "mqtt_config.py")),
        ("mqtt_publisher.py", os.path.join(backend_path, "mqtt_publisher.py")),
        ("mqtt_subscriber.py", os.path.join(backend_path, "mqtt_subscriber.py")),
    ]
    
    all_found = True
    for name, path in files_to_check:
        if os.path.exists(path):
            print(f"✅ {name} found")
        else:
            print(f"❌ {name} NOT found at {path}")
            all_found = False
    
    return all_found


def check_mqtt_config():
    """Check if MQTT config can be imported"""
    print_section("4. Checking MQTT Configuration")
    
    try:
        # Try to import mqtt_config
        backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
        sys.path.insert(0, backend_path)
        
        import mqtt_config
        
        print(f"✅ mqtt_config.py loaded successfully")
        print(f"\n   MQTT Broker: {mqtt_config.MQTT_BROKER}:{mqtt_config.MQTT_PORT}")
        print(f"   Topics:")
        print(f"     - Sensor Data:     {mqtt_config.MQTT_TOPIC_SENSOR_DATA}")
        print(f"     - Health Analysis: {mqtt_config.MQTT_TOPIC_HEALTH_ANALYSIS}")
        print(f"     - Status:          {mqtt_config.MQTT_TOPIC_STATUS}")
        print(f"   Publisher ID: {mqtt_config.PUBLISHER_ID}")
        print(f"   Subscriber ID: {mqtt_config.SUBSCRIBER_ID}")
        print(f"   Data Path: {mqtt_config.SUBSCRIBER_DB_PATH}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import mqtt_config: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Error checking config: {e}")
        return False


def main():
    """Run all checks"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║         MQTT Setup Verification Tool                  ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    results = {
        "Mosquitto": check_mosquitto(),
        "paho-mqtt": check_paho_mqtt(),
        "MQTT Files": check_mqtt_files(),
        "MQTT Config": check_mqtt_config(),
    }
    
    print_section("Summary")
    
    all_pass = True
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
        if not result:
            all_pass = False
    
    if all_pass:
        print("\n🎉 All checks passed! Ready to run MQTT setup.")
        print("\nNext steps:")
        print("  1. Terminal 1: mosquitto")
        print("  2. Terminal 2: python backend/mqtt_publisher.py")
        print("  3. Terminal 3: python backend/mqtt_subscriber.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. See above for instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
