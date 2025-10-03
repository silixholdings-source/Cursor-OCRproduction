#!/usr/bin/env python3
"""
Main entry point for the AI ERP SaaS Backend
This file imports the FastAPI app from src/main.py for easy deployment
"""

import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import the FastAPI app from src/main.py
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
