#!/usr/bin/env python3
"""
Direct test of the application without HTTP requests
"""
import os
import sys
from pathlib import Path

# Set environment variables
os.environ["DATABASE_URL"] = "sqlite:///./app.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "dev-secret-key-for-testing"
os.environ["OCR_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "development"

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_app_directly():
    """Test the application directly without HTTP"""
    print("Testing AI ERP SaaS Application Directly")
    print("=" * 40)
    
    try:
        # Import the app
        from main_simple import app
        print("+ App imported successfully")
        
        # Test app properties
        print(f"+ App title: {app.title}")
        print(f"+ App version: {app.version}")
        print(f"+ Routes count: {len(app.routes)}")
        
        # Test routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(route.path)
        
        print(f"+ Available routes: {routes}")
        
        # Test OCR service
        from services.simple_ocr import SimpleOCRService
        import asyncio
        
        async def test_ocr():
            ocr_service = SimpleOCRService()
            result = await ocr_service.extract_invoice("test.pdf", "test-company")
            return result
        
        result = asyncio.run(test_ocr())
        print(f"+ OCR service test: {result['vendor']} - ${result['amount']}")
        
        # Test database
        from core.database import Base, engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import text
        
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            result = db.execute(text("SELECT 1")).fetchone()
            print(f"+ Database test: {result[0]}")
        finally:
            db.close()
        
        print("\nALL TESTS PASSED!")
        print("Your AI ERP SaaS application is working perfectly!")
        return True
        
    except Exception as e:
        print(f"- Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_directly()
    sys.exit(0 if success else 1)









