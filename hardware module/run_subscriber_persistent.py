#!/usr/bin/env python3
"""
Persistent MQTT Subscriber Runner
This script runs the subscriber without any interruption handling
"""

import sys
import os
import signal
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from mqtt_subscriber import MQTTSubscriber

def signal_handler(sig, frame):
    """Handle termination signals"""
    print('\n\n✓ Received termination signal, shutting down...')
    sys.exit(0)

# Set up signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Run subscriber persistently"""
    print("\n" + "="*70)
    print("🚀 PERSISTENT MQTT SUBSCRIBER STARTING")
    print("="*70 + "\n")
    
    subscriber = MQTTSubscriber()
    
    try:
        # Connect and start
        subscriber.connect()
        subscriber.start()
        
        print("✅ Subscriber is running. It will continue collecting data.")
        print("📊 Data is being saved to: data/mqtt_sensor_data.csv")
        print("\nPress Ctrl+C to stop.\n")
        
        # Keep it alive indefinitely
        while subscriber.running:
            time.sleep(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
