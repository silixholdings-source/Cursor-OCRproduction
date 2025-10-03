#!/usr/bin/env python3
"""
Final application test - tests the running server
"""
import requests
import time
import sys

def test_server_endpoints():
    """Test all available endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== Testing AI ERP SaaS Application ===")
    print(f"Testing server at: {base_url}")
    print()
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/ready", "Readiness check"),
        ("/live", "Liveness check"),
        ("/docs", "API documentation"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, description in endpoints:
        try:
            print(f"Testing {endpoint} ({description})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"  + {endpoint} - Status: {response.status_code}")
                if endpoint in ["/health", "/ready", "/live"]:
                    data = response.json()
                    print(f"     Response: {data}")
                passed += 1
            else:
                print(f"  - {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  - {endpoint} - Connection failed (server not running?)")
        except requests.exceptions.Timeout:
            print(f"  - {endpoint} - Request timeout")
        except Exception as e:
            print(f"  - {endpoint} - Error: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\nALL TESTS PASSED!")
        print("Your AI ERP SaaS application is working perfectly!")
        return True
    else:
        print(f"\n{total - passed} tests failed")
        print("Some issues detected")
        return False

if __name__ == "__main__":
    success = test_server_endpoints()
    sys.exit(0 if success else 1)
