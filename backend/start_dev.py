#!/usr/bin/env python3
"""
Development startup script for the AI ERP SaaS application
This script sets up the database and starts the FastAPI server
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description, check=True):
    """Run a shell command with logging"""
    logger.info(f"Running: {description}")
    logger.debug(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Stderr: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        if check:
            raise
        return e

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ is required")
        return False
    
    # Check if we're in the right directory
    if not Path("src").exists():
        logger.error("Please run this script from the backend directory")
        return False
    
    logger.info("✅ Dependencies check passed")
    return True

def setup_database():
    """Set up the database with migrations"""
    logger.info("Setting up database...")
    
    try:
        # Check if alembic is initialized
        if not Path("alembic").exists():
            logger.info("Initializing Alembic...")
            run_command("alembic init alembic", "Initialize Alembic")
        
        # Run migrations
        logger.info("Running database migrations...")
        run_command("alembic upgrade head", "Run database migrations")
        
        logger.info("✅ Database setup completed")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    try:
        run_command("pip install -r requirements.txt", "Install requirements")
        logger.info("✅ Dependencies installed")
        return True
        
    except Exception as e:
        logger.error(f"Dependency installation failed: {e}")
        return False

def start_application():
    """Start the FastAPI application"""
    logger.info("Starting FastAPI application...")
    
    try:
        # Set environment variables for development
        env = os.environ.copy()
        env["ENVIRONMENT"] = "development"
        env["DEBUG"] = "true"
        
        # Start the application
        command = [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        
        logger.info("Starting server with: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
        logger.info("API documentation will be available at: http://localhost:8000/docs")
        logger.info("Press Ctrl+C to stop the server")
        
        subprocess.run(command, env=env)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")

def main():
    """Main startup function"""
    logger.info("🚀 Starting AI ERP SaaS Development Environment")
    logger.info("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        logger.warning("Dependency installation failed, continuing anyway...")
    
    # Setup database
    if not setup_database():
        logger.warning("Database setup failed, continuing anyway...")
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
