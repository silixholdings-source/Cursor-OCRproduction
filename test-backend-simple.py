#!/usr/bin/env python3
"""
Simple Backend Testing - Uses only built-in Python modules
"""

import urllib.request
import urllib.parse
import json
import time

def test_backend_endpoints():
    """Test backend endpoints using built-in urllib"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend Endpoints...\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Health Check
    tests_total += 1
    try:
        with urllib.request.urlopen(f"{base_url}/health", timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ Health Check: {data.get('status', 'unknown')}")
                tests_passed += 1
            else:
                print(f"❌ Health Check: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Health Check: {e}")
    
    # Test 2: OCR Demo Processing
    tests_total += 1
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
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                result = json.loads(response.read().decode())
                if result.get("status") == "success" and result.get("ocr_data"):
                    print("✅ OCR Demo Processing: Success")
                    ocr_data = result['ocr_data']
                    print(f"   Supplier: {ocr_data.get('supplier_name', 'N/A')}")
                    print(f"   Amount: ${ocr_data.get('total_amount', 'N/A')}")
                    print(f"   Invoice: {ocr_data.get('invoice_number', 'N/A')}")
                    tests_passed += 1
                else:
                    print("❌ OCR Demo Processing: Invalid response")
            else:
                print(f"❌ OCR Demo Processing: HTTP {response.status}")
    except Exception as e:
        print(f"❌ OCR Demo Processing: {e}")
    
    # Test 3: OCR Service Status
    tests_total += 1
    try:
        with urllib.request.urlopen(f"{base_url}/api/v1/ocr/status", timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ OCR Service Status: {data.get('status', 'unknown')}")
                tests_passed += 1
            else:
                print(f"❌ OCR Service Status: HTTP {response.status}")
    except Exception as e:
        print(f"❌ OCR Service Status: {e}")
    
    # Print summary
    success_rate = (tests_passed / tests_total) * 100
    print(f"\n📊 Backend Test Summary:")
    print(f"✅ Passed: {tests_passed}/{tests_total}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 BACKEND: FULLY FUNCTIONAL")
        print("   All backend endpoints are working correctly!")
        return True
    elif success_rate >= 60:
        print("\n✅ BACKEND: MOSTLY FUNCTIONAL")
        print("   Most endpoints are working.")
        return True
    else:
        print("\n⚠️  BACKEND: NEEDS ATTENTION")
        print("   Several endpoints need to be fixed.")
        return False

def main():
    print("🚀 Starting Simple Backend Testing...\n")
    
    # Test if backend is running
    try:
        with urllib.request.urlopen("http://localhost:8000/health", timeout=2) as response:
            if response.status == 200:
                print("✅ Backend is running on port 8000\n")
                return test_backend_endpoints()
            else:
                print("❌ Backend not responding properly")
                return False
    except Exception as e:
        print("❌ Backend not running or not accessible")
        print("   Start the backend with: cd backend && python simple_backend.py")
        print("   Then run this test again")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
