#!/usr/bin/env python3
"""
Quick setup and test script for Soil Health Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or version.minor < 8:
        print("❌ Python 3.8+ required")
        return False
    print("✓ Python version OK")
    return True

def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    dirs = ['data', 'models', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ {dir_name}/ directory ready")
    return True

def verify_csv():
    """Verify training data CSV"""
    print_header("Verifying Training Data")
    csv_path = Path('data/data.csv')
    if not csv_path.exists():
        print("❌ CSV file not found at data/data.csv")
        return False
    
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        print(f"✓ CSV loaded: {len(df)} records")
        print(f"  Columns: {', '.join(df.columns)}")
        print(f"  Date range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
        return True
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def train_model():
    """Train ML models"""
    print_header("Training ML Models")
    try:
        from soil_health_ml import SoilHealthAnalyzer
        
        analyzer = SoilHealthAnalyzer()
        if analyzer.train_on_csv('data/data.csv'):
            analyzer.save_model('models')
            print("✓ Models trained and saved")
            return True
        else:
            print("❌ Model training failed")
            return False
    except Exception as e:
        print(f"❌ Error during training: {e}")
        return False

def test_models():
    """Test trained models"""
    print_header("Testing Models")
    try:
        from soil_health_ml import SoilHealthAnalyzer
        
        analyzer = SoilHealthAnalyzer()
        if not analyzer.load_model('models'):
            print("❌ Failed to load models")
            return False
        
        # Test with sample reading
        test_reading = {
            'N': 22,
            'P': 18,
            'K': 150,
            'CO2': 500,
            'Temperature': 22,
            'Moisture': 55,
            'pH': 7.2
        }
        
        print("\nTest Sensor Reading:")
        for key, value in test_reading.items():
            print(f"  {key}: {value}")
        
        analysis = analyzer.analyze_reading(test_reading)
        print("\nAnalysis Results:")
        print(f"  Health Index: {analysis['soil_health_index']}/100")
        print(f"  Health Status: {analysis['health_status']}")
        print(f"  Anomalous: {analysis['is_anomalous']}")
        print(f"  Anomaly Score: {analysis['anomaly_score']:.3f}")
        print(f"  Critical Factors: {len(analysis['critical_factors'])}")
        if analysis['critical_factors']:
            for factor in analysis['critical_factors']:
                print(f"    - {factor}")
        
        print("\n✓ Model test successful")
        return True
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api():
    """Test API endpoints"""
    print_header("Testing API Endpoints")
    try:
        import requests
        import time
        
        # Start server in background
        print("Note: Run 'python app.py' in another terminal to test API endpoints")
        print("Then run: python test_api.py")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all setup steps"""
    print_header("SOIL HEALTH BACKEND - SETUP & TEST")
    
    steps = [
        ("Python Version", check_python_version),
        ("Create Directories", create_directories),
        ("Verify Training Data", verify_csv),
        ("Install Dependencies", install_dependencies),
        ("Train Models", train_model),
        ("Test Models", test_models),
    ]
    
    results = []
    for name, func in steps:
        try:
            result = func()
            results.append((name, result))
            if not result:
                print(f"\n⚠️  {name} failed. Continuing...")
        except Exception as e:
            print(f"\n❌ {name} error: {e}")
            results.append((name, False))
    
    # Summary
    print_header("SETUP SUMMARY")
    for name, result in results:
        status = "✓" if result else "❌"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All setup steps completed successfully!")
        print("\nNext steps:")
        print("1. Start the Flask API server:")
        print("   python app.py")
        print("\n2. Test the API (in another terminal):")
        print("   python test_api.py")
        print("\n3. Configure frontend at:")
        print("   VITE_API_URL=http://localhost:5000/api")
    else:
        print(f"\n⚠️  {total - passed} step(s) failed. Please review and retry.")

if __name__ == "__main__":
    main()
