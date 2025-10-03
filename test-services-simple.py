#!/usr/bin/env python3
"""
Simple Service Test - Tests Frontend and Backend (No Unicode)
"""

import urllib.request
import urllib.parse
import json
import time

def test_service(url, name):
    """Test a service endpoint"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                print(f"SUCCESS: {name} - Working (HTTP {response.status})")
                return True
            else:
                print(f"FAILED: {name} - HTTP {response.status}")
                return False
    except Exception as e:
        print(f"FAILED: {name} - Connection error: {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Backend API:")
    print("===================")
    
    # Test health endpoint
    health_ok = test_service(f"{base_url}/health", "Backend Health")
    
    # Test OCR demo endpoint
    try:
        payload = {
            "test": True,
            "file_name": "test-invoice.pdf",
            "company_id": "test-company"
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{base_url}/api/v1/processing/demo",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                result = json.loads(response.read().decode())
                if result.get("status") == "success":
                    print("SUCCESS: Backend OCR Demo - Working")
                    return True
                else:
                    print("FAILED: Backend OCR Demo - Invalid response")
                    return False
            else:
                print(f"FAILED: Backend OCR Demo - HTTP {response.status}")
                return False
    except Exception as e:
        print(f"FAILED: Backend OCR Demo - Connection error: {e}")
        return False

def test_frontend():
    """Test frontend access"""
    base_url = "http://localhost:3000"
    
    print("\nTesting Frontend:")
    print("=================")
    
    # Test main page
    main_ok = test_service(f"{base_url}/", "Frontend Main Page")
    
    # Test OCR pages
    ocr_pages = [
        "/ocr-test",
        "/test-ocr",
        "/demo",
        "/debug-ocr"
    ]
    
    ocr_ok = 0
    for page in ocr_pages:
        if test_service(f"{base_url}{page}", f"OCR Page {page}"):
            ocr_ok += 1
    
    return main_ok and ocr_ok > 0

def main():
    print("Testing AI ERP SaaS Application\n")
    
    # Test backend
    backend_ok = test_backend_api()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Summary
    print(f"\nTest Summary:")
    print(f"=============")
    print(f"Backend: {'Working' if backend_ok else 'Failed'}")
    print(f"Frontend: {'Working' if frontend_ok else 'Failed'}")
    
    if backend_ok and frontend_ok:
        print(f"\nRESULT: APPLICATION IS FULLY FUNCTIONAL!")
        print(f"   Both frontend and backend are working.")
        print(f"   You can now test the OCR functionality.")
        print(f"\nAccess URLs:")
        print(f"   Frontend: http://localhost:3000")
        print(f"   Backend:  http://localhost:8000")
        print(f"\nOCR Testing Pages:")
        print(f"   http://localhost:3000/ocr-test")
        print(f"   http://localhost:3000/test-ocr")
        print(f"   http://localhost:3000/demo")
        return True
    else:
        print(f"\nRESULT: APPLICATION NEEDS ATTENTION")
        print(f"   Some services are not working properly.")
        if not backend_ok:
            print(f"   - Backend is not responding")
        if not frontend_ok:
            print(f"   - Frontend is not accessible")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
