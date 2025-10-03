#!/usr/bin/env python3
"""
Simple import test for AI ERP SaaS application
"""
import sys
import os
from datetime import datetime

def test_core_imports():
    """Test core system imports"""
    print("🔍 Testing core system imports...")
    try:
        from core.config import settings
        from core.database import engine, get_db
        from core.security import SecurityManager
        from core.health_checks import HealthChecker
        print("✅ Core system imports successful")
        return True
    except Exception as e:
        print(f"❌ Core imports failed: {e}")
        return False

def test_models():
    """Test database models"""
    print("🔍 Testing database models...")
    try:
        from src.models.user import User, UserRole, UserStatus
        from src.models.company import Company, CompanyStatus, CompanyTier
        from src.models.invoice import Invoice, InvoiceStatus, InvoiceType
        from src.models.audit import AuditLog, AuditAction, AuditResourceType
        print("✅ Database models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model imports failed: {e}")
        return False

def test_schemas():
    """Test Pydantic schemas"""
    print("🔍 Testing Pydantic schemas...")
    try:
        from schemas.billing import BillingInvoiceResponse, SubscriptionResponse
        from schemas.analytics import MLModelHealth, CashFlowPrediction
        from schemas.invoice import InvoiceResponse, InvoiceCreateRequest
        from schemas.auth import UserLoginRequest, UserResponse
        print("✅ Pydantic schemas imported successfully")
        return True
    except Exception as e:
        print(f"❌ Schema imports failed: {e}")
        return False

def test_services():
    """Test business services"""
    print("🔍 Testing business services...")
    try:
        from services.billing import StripeService
        from services.ocr import OCRService
        from services.ml_training import MLTrainingService
        from services.erp_integration import ERPIntegrationService
        print("✅ Business services imported successfully")
        return True
    except Exception as e:
        print(f"❌ Service imports failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoint imports"""
    print("🔍 Testing API endpoints...")
    try:
        from api.v1.endpoints import health, auth, invoices, companies, users, erp, processing, ocr, database, analytics, billing
        print("✅ API endpoints imported successfully")
        return True
    except Exception as e:
        print(f"❌ API endpoint imports failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI application creation"""
    print("🔍 Testing FastAPI application...")
    try:
        from main import app
        print("✅ FastAPI application created successfully")
        
        # Test that the app has the expected routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/api/v1/health", "/api/v1/auth", "/api/v1/invoices"]
        
        for expected_route in expected_routes:
            if any(expected_route in route for route in routes):
                print(f"   ✅ Route {expected_route} found")
            else:
                print(f"   ⚠️  Route {expected_route} not found")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI app test failed: {e}")
        return False

def test_security_features():
    """Test security features"""
    print("🔍 Testing security features...")
    try:
        from core.security import SecurityManager
        from core.security_headers import SecurityHeadersMiddleware
        from core.rate_limiting import RateLimitingMiddleware
        
        # Test security manager
        security_manager = SecurityManager()
        print("✅ Security manager initialized")
        
        # Test security headers
        print("✅ Security headers middleware available")
        
        # Test rate limiting
        print("✅ Rate limiting middleware available")
        
        return True
    except Exception as e:
        print(f"❌ Security features test failed: {e}")
        return False

def generate_test_report():
    """Generate test report"""
    print("\n" + "="*60)
    print("🏆 AI ERP SaaS - IMPORT TEST REPORT")
    print("="*60)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results
    tests = [
        ("Core System Imports", test_core_imports()),
        ("Database Models", test_models()),
        ("Pydantic Schemas", test_schemas()),
        ("Business Services", test_services()),
        ("API Endpoints", test_api_endpoints()),
        ("FastAPI Application", test_fastapi_app()),
        ("Security Features", test_security_features()),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print("📊 TEST RESULTS:")
    print("-" * 40)
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print("-" * 40)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ APPLICATION IMPORTS ARE WORKING!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed")
        print("❌ Application has import issues")
        return False

if __name__ == "__main__":
    print("🚀 AI ERP SaaS - Import Test")
    print("=" * 60)
    
    success = generate_test_report()
    
    if success:
        print("\n🎯 STATUS: IMPORTS WORKING ✅")
        sys.exit(0)
    else:
        print("\n🎯 STATUS: IMPORT ISSUES ❌")
        sys.exit(1)

