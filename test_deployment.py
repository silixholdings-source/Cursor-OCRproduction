"""
Test script for deployed OCR service on Render
"""
import requests
import json
import time
from pathlib import Path

def test_deployed_service(render_url):
    """Test the deployed OCR service on Render"""
    
    print(f"🧪 Testing deployed OCR service at: {render_url}")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        response = requests.get(f"{render_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Service: {health_data.get('service', 'Unknown')}")
            print(f"   ✅ Version: {health_data.get('version', 'Unknown')}")
            print(f"   ✅ Provider: {health_data.get('provider', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Root Endpoint
    print("\n2️⃣ Testing Root Endpoint...")
    try:
        response = requests.get(f"{render_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            root_data = response.json()
            print(f"   ✅ Service: {root_data.get('service', 'Unknown')}")
            print(f"   ✅ Status: {root_data.get('status', 'Unknown')}")
            print(f"   ✅ Available endpoints: {len(root_data.get('endpoints', {}))}")
        else:
            print(f"   ❌ Root endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Readiness Check
    print("\n3️⃣ Testing Readiness Endpoint...")
    try:
        response = requests.get(f"{render_url}/ready", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            ready_data = response.json()
            print(f"   ✅ Ready status: {ready_data.get('status', 'Unknown')}")
        else:
            print(f"   ❌ Readiness check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Readiness check error: {e}")
    
    # Test 4: API Documentation
    print("\n4️⃣ Testing API Documentation...")
    try:
        response = requests.get(f"{render_url}/docs", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API documentation is accessible")
        else:
            print(f"   ❌ API docs failed: {response.text}")
    except Exception as e:
        print(f"   ❌ API docs error: {e}")
    
    # Test 5: OCR Endpoint (without file)
    print("\n5️⃣ Testing OCR Endpoint (no file)...")
    try:
        response = requests.post(f"{render_url}/ocr", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 422:  # Expected validation error
            print("   ✅ OCR endpoint properly validates input (no file provided)")
        else:
            print(f"   ⚠️  Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ OCR endpoint error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Testing Summary:")
    print(f"   Service URL: {render_url}")
    print("   ✅ Basic connectivity tests completed")
    print("   📖 API docs available at: {render_url}/docs")
    print("   🔧 Ready for OCR file upload testing")

def test_ocr_with_file(render_url, file_path):
    """Test OCR endpoint with actual file upload"""
    
    print(f"\n🧪 Testing OCR with file: {file_path}")
    print("=" * 60)
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
            data = {
                'language': 'eng',
                'confidence_threshold': 0.8
            }
            
            print(f"   📤 Uploading file: {Path(file_path).name}")
            response = requests.post(
                f"{render_url}/ocr", 
                files=files, 
                data=data, 
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ OCR processing successful!")
                print(f"   📄 Extracted text: {result.get('text', '')[:200]}...")
                print(f"   🎯 Confidence: {result.get('confidence', 0):.2f}")
                print(f"   ⏱️  Processing time: {result.get('processing_time', 0):.2f}s")
                print(f"   📁 File type: {result.get('file_type', 'Unknown')}")
            else:
                print(f"   ❌ OCR processing failed: {response.text}")
                
    except Exception as e:
        print(f"   ❌ File upload error: {e}")

def main():
    """Main testing function"""
    
    # Replace with your actual Render service URL
    render_url = input("Enter your Render service URL (e.g., https://your-service.onrender.com): ").strip()
    
    if not render_url:
        print("❌ No URL provided. Exiting.")
        return
    
    if not render_url.startswith('http'):
        render_url = f"https://{render_url}"
    
    # Basic service tests
    test_deployed_service(render_url)
    
    # Optional: Test with file upload
    test_file = input("\nEnter path to test file (image/PDF) or press Enter to skip: ").strip()
    if test_file:
        test_ocr_with_file(render_url, test_file)
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    main()
