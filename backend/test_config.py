"""
Test configuration for the AI ERP SaaS application.
This overrides the main configuration to use SQLite for testing.
"""
import os
from pathlib import Path

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["OCR_PROVIDER"] = "mock"
os.environ["ENVIRONMENT"] = "test"

# Import the main config after setting environment variables
from src.core.config import settings

# Override settings for testing
settings.DATABASE_URL = "sqlite:///./test.db"
settings.REDIS_URL = "redis://localhost:6379"
settings.SECRET_KEY = "test-secret-key-for-testing-only"
settings.OCR_PROVIDER = "mock"
settings.ENVIRONMENT = "test"
