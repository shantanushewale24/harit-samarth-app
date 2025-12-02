#!/usr/bin/env python3
"""
Test script for Soil Health Backend API
Run this after starting: python app.py
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:5000"

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_json(data):
    """Pretty print JSON"""
    print(json.dumps(data, indent=2))

def test_health_check():
    """Test health check endpoint"""
    print_header("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Server is running")
            print_json(response.json())
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except requests.ConnectionError:
        print_error("Could not connect to server at http://localhost:5000")
        print_info("Make sure Flask server is running: python app.py")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_analyze_soil():
    """Test soil analysis"""
    print_header("Analyze Soil - Healthy Reading")
    
    # Healthy reading
    healthy_reading = {
        "N": 22,
        "P": 18,
        "K": 150,
        "CO2": 500,
        "Temperature": 22,
        "Moisture": 55,
        "pH": 7.2
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-health/analyze",
            json=healthy_reading,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Analysis completed")
            data = response.json()
            print(f"  Health Index: {data['soil_health_index']}/100")
            print(f"  Health Status: {data['health_status']}")
            print(f"  Anomalous: {data['is_anomalous']}")
            print(f"  Anomaly Score: {data['anomaly_score']:.3f}")
            print(f"  Critical Factors: {len(data['critical_factors'])}")
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            print_json(response.json())
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_analyze_unhealthy():
    """Test with unhealthy reading"""
    print_header("Analyze Soil - Unhealthy Reading")
    
    # Unhealthy reading (low N, high moisture)
    unhealthy_reading = {
        "N": 8,
        "P": 22,
        "K": 180,
        "CO2": 450,
        "Temperature": 28,
        "Moisture": 72,
        "pH": 8.2
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-health/analyze",
            json=unhealthy_reading,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Analysis completed")
            data = response.json()
            print(f"  Health Index: {data['soil_health_index']}/100")
            print(f"  Health Status: {data['health_status']}")
            print(f"  Critical Factors: {len(data['critical_factors'])}")
            if data['critical_factors']:
                for factor in data['critical_factors'][:3]:  # Show first 3
                    print(f"    - {factor}")
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_health_index():
    """Test health index endpoint"""
    print_header("Get Health Index")
    
    reading = {
        "N": 22,
        "P": 18,
        "K": 150,
        "CO2": 500,
        "Temperature": 22,
        "Moisture": 55,
        "pH": 7.2
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-health/health-index",
            json=reading,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Health index retrieved")
            data = response.json()
            print_json(data)
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_anomaly_detection():
    """Test anomaly detection"""
    print_header("Anomaly Detection - Normal Reading")
    
    normal_reading = {
        "N": 22,
        "P": 18,
        "K": 150,
        "CO2": 500,
        "Temperature": 22,
        "Moisture": 55,
        "pH": 7.2
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-health/anomaly",
            json=normal_reading,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Anomaly detection completed")
            data = response.json()
            print_json(data)
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_critical_factors():
    """Test critical factors endpoint"""
    print_header("Critical Factors")
    
    reading = {
        "N": 8,      # Low nitrogen
        "P": 22,
        "K": 180,
        "CO2": 450,
        "Temperature": 32,  # High temperature
        "Moisture": 72,     # High moisture
        "pH": 8.2   # High pH
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-health/critical-factors",
            json=reading,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Critical factors identified")
            data = response.json()
            print(f"  Status: {data['status']}")
            print(f"  Factors: {data['factor_count']}")
            for factor in data['critical_factors']:
                print(f"    - {factor}")
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_optimal_ranges():
    """Test optimal ranges endpoint"""
    print_header("Get Optimal Ranges")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/soil-health/optimal-ranges",
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Optimal ranges retrieved")
            data = response.json()
            ranges = data['optimal_ranges']
            for param, info in ranges.items():
                print(f"  {param}: {info['min']}-{info['max']} {info['unit']}")
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_batch_analyze():
    """Test batch analysis"""
    print_header("Batch Analysis")
    
    readings = [
        {
            "N": 22, "P": 18, "K": 150, "CO2": 500,
            "Temperature": 22, "Moisture": 55, "pH": 7.2
        },
        {
            "N": 20, "P": 16, "K": 145, "CO2": 510,
            "Temperature": 21, "Moisture": 52, "pH": 7.1
        },
        {
            "N": 24, "P": 20, "K": 155, "CO2": 490,
            "Temperature": 23, "Moisture": 58, "pH": 7.3
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/soil-health/batch-analyze",
            json={"readings": readings},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Batch analysis completed")
            data = response.json()
            print(f"  Readings analyzed: {data['count']}")
            for i, analysis in enumerate(data['analyses']):
                print(f"  Reading {i+1}: {analysis['soil_health_index']} - {analysis['health_status']}")
            return True
        else:
            print_error(f"Server returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def performance_test():
    """Test API performance"""
    print_header("Performance Test")
    
    reading = {
        "N": 22, "P": 18, "K": 150, "CO2": 500,
        "Temperature": 22, "Moisture": 55, "pH": 7.2
    }
    
    num_requests = 10
    times = []
    
    try:
        print_info(f"Sending {num_requests} requests...")
        for i in range(num_requests):
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/api/soil-health/analyze",
                json=reading,
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            if response.status_code != 200:
                print_error(f"Request {i+1} failed")
                return False
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print_success(f"All requests completed")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("SOIL HEALTH BACKEND - API TEST SUITE")
    
    tests = [
        ("Health Check", test_health_check),
        ("Analyze Soil (Healthy)", test_analyze_soil),
        ("Analyze Soil (Unhealthy)", test_analyze_unhealthy),
        ("Get Health Index", test_health_index),
        ("Anomaly Detection", test_anomaly_detection),
        ("Critical Factors", test_critical_factors),
        ("Get Optimal Ranges", test_optimal_ranges),
        ("Batch Analysis", test_batch_analyze),
        ("Performance Test", performance_test),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    for name, result in results:
        status = f"{Colors.OKGREEN}✓{Colors.ENDC}" if result else f"{Colors.FAIL}✗{Colors.ENDC}"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}All tests passed!{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{total - passed} test(s) failed{Colors.ENDC}")

if __name__ == "__main__":
    main()
