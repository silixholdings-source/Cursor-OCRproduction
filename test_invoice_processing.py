#!/usr/bin/env python3
"""
Test script to verify invoice processing functionality
"""
import requests
import json
import io

def test_ocr_upload():
    """Test the OCR upload endpoint"""
    print("=== Testing OCR Upload Endpoint ===")
    
    # Create a fake PDF content
    fake_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test Invoice) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
    
    # Test the upload endpoint
    files = {'file': ('test_invoice.pdf', fake_pdf_content, 'application/pdf')}
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/ocr/upload', files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if we got the expected structure
            if result.get('success') and result.get('data', {}).get('extracted_data'):
                print("✅ OCR data extracted successfully!")
                extracted_data = result['data']['extracted_data']
                print(f"Extracted data keys: {list(extracted_data.keys())}")
                return True
            else:
                print("❌ Unexpected response structure")
                return False
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def test_frontend_connection():
    """Test if frontend can connect to backend"""
    print("\n=== Testing Frontend-Backend Connection ===")
    
    try:
        # Test health endpoint
        health_response = requests.get('http://127.0.0.1:8000/health')
        print(f"Backend health: {health_response.status_code}")
        
        # Test frontend
        frontend_response = requests.get('http://localhost:3001/dashboard/invoices')
        print(f"Frontend invoices page: {frontend_response.status_code}")
        
        if health_response.status_code == 200 and frontend_response.status_code == 200:
            print("✅ Both frontend and backend are accessible!")
            return True
        else:
            print("❌ Connection issues detected")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Invoice Processing Functionality\n")
    
    tests = [
        ("Frontend-Backend Connection", test_frontend_connection),
        ("OCR Upload Endpoint", test_ocr_upload),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Invoice processing should be working.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)









