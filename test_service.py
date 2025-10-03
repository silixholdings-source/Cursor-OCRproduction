"""
Test script for OCR service
"""
import requests
import json

def test_service():
    base_url = "http://localhost:8002"
    
    print("Testing OCR Service...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Root endpoint failed: {e}")
    
    # Test docs endpoint
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Docs endpoint: {response.status_code}")
        if response.status_code == 200:
            print("API documentation is available")
    except Exception as e:
        print(f"Docs endpoint failed: {e}")

if __name__ == "__main__":
    test_service()
