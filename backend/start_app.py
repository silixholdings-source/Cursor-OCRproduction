#!/usr/bin/env python3
"""
Simple startup script for the AI ERP SaaS application
"""
import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set environment variables for development
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/app.db")

if __name__ == "__main__":
    try:
        # Test imports
        print("Testing imports...")
        
        from core.config import settings
        print("✅ Config import works")
        
        from core.database import engine, Base
        print("✅ Database import works")
        
        # Create database directory if it doesn't exist
        data_dir = Path("./data")
        data_dir.mkdir(exist_ok=True)
        
        # Create tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
        
        # Start the app
        print("Starting FastAPI application...")
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["src"]
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)








