#!/usr/bin/env python3
"""
Direct Backend Testing - Tests the simple backend directly
"""

import asyncio
import aiohttp
import json
import time

async def test_backend_endpoints():
    """Test backend endpoints directly"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend Endpoints Directly...\n")
    
    tests_passed = 0
    tests_total = 0
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health Check
        tests_total += 1
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
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
            async with session.post(
                f"{base_url}/api/v1/processing/demo",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success" and data.get("ocr_data"):
                        print("✅ OCR Demo Processing: Success")
                        print(f"   Supplier: {data['ocr_data'].get('supplier_name', 'N/A')}")
                        print(f"   Amount: ${data['ocr_data'].get('total_amount', 'N/A')}")
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
            async with session.get(f"{base_url}/api/v1/ocr/status") as response:
                if response.status == 200:
                    data = await response.json()
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
    elif success_rate >= 60:
        print("\n✅ BACKEND: MOSTLY FUNCTIONAL")
        print("   Most endpoints are working.")
    else:
        print("\n⚠️  BACKEND: NEEDS ATTENTION")
        print("   Several endpoints need to be fixed.")
    
    return success_rate >= 80

async def main():
    print("🚀 Starting Direct Backend Testing...\n")
    
    # Test if backend is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health", timeout=aiohttp.ClientTimeout(total=2)) as response:
                if response.status == 200:
                    print("✅ Backend is running on port 8000\n")
                    await test_backend_endpoints()
                else:
                    print("❌ Backend not responding properly")
    except Exception as e:
        print("❌ Backend not running or not accessible")
        print("   Start the backend with: cd backend && python simple_backend.py")
        print("   Then run this test again")

if __name__ == "__main__":
    asyncio.run(main())
