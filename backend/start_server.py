#!/usr/bin/env python3
"""
Server startup script for AI ERP SaaS application
This script properly sets up the environment and starts the server
"""
import os
import sys
from pathlib import Path

# Set environment variables for local testing
os.environ["DATABASE_URL"] = "sqlite:///./app.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "dev-secret-key-for-testing"
os.environ["OCR_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "development"

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import and run the application
if __name__ == "__main__":
    import uvicorn
    from main_simple import app
    
    print("Starting AI ERP SaaS Application...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        "main_simple:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
