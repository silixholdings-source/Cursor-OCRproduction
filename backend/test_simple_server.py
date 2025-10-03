#!/usr/bin/env python3
"""
Simple server test without Unicode issues
"""
import requests
import time
import sys

def test_server():
    """Test the running server"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing AI ERP SaaS Application")
    print("=" * 40)
    print(f"Server URL: {base_url}")
    print()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/ready", "Readiness check"),
        ("/live", "Liveness check"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, description in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"  + PASS - Status: {response.status_code}")
                if endpoint in ["/health", "/ready", "/live"]:
                    data = response.json()
                    print(f"    Data: {data}")
                passed += 1
            else:
                print(f"  - FAIL - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  - FAIL - Connection failed")
        except requests.exceptions.Timeout:
            print(f"  - FAIL - Timeout")
        except Exception as e:
            print(f"  - FAIL - Error: {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\nSUCCESS: All tests passed!")
        return True
    else:
        print(f"\nFAILED: {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)









