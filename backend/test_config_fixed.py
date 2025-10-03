"""
Fixed test configuration for AI ERP SaaS application
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database configuration - Use PostgreSQL for testing to support UUID
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/ai_erp_test"

# Create test engine with proper PostgreSQL configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False  # Disable SQL echo in tests
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)