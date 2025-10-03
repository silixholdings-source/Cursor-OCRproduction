"""
Test configuration and fixtures for ERP adapter testing
"""
import uuid
from typing import Dict, Any


def get_test_connection_config(erp_type: str = "dynamics_gp") -> Dict[str, Any]:
    """Get test connection configuration for ERP adapters"""
    
    configs = {
        "dynamics_gp": {
            "base_url": "http://test-dynamics-gp.local",
            "api_key": "test-api-key-12345",
            "company_id": "TEST_COMPANY",
            "timeout": 30,
            "database_name": "TEST_DB"
        },
        "dynamics_365_bc": {
            "base_url": "https://api.businesscentral.dynamics.com",
            "tenant_id": "test-tenant-id",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "environment": "test-environment",
            "company_id": "test-company-id",
            "access_token": "test-access-token",
            "api_key": "test-api-key"
        },
        "xero": {
            "base_url": "https://api.xero.com",
            "api_key": "test-api-key",
            "company_id": "test-company-id",
            "tenant_id": "test-tenant-id",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "access_token": "test-access-token"
        },
        "quickbooks": {
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "redirect_uri": "http://localhost:8000/auth/callback",
            "environment": "sandbox"
        },
        "sage": {
            "base_url": "https://api.sage.com",
            "api_key": "test-api-key",
            "company_id": "test-company-id"
        }
    }
    
    return configs.get(erp_type, configs["dynamics_gp"])


def get_test_invoice_data() -> Dict[str, Any]:
    """Get test invoice data"""
    return {
        "id": str(uuid.uuid4()),
        "invoice_number": "TEST-INV-001",
        "supplier_name": "Test Supplier Ltd",
        "supplier_email": "test@supplier.com",
        "supplier_phone": "+1234567890",
        "supplier_address": "123 Test Street, Test City, TC 12345",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-15",
        "total_amount": 1000.00,
        "currency": "USD",
        "tax_amount": 80.00,
        "tax_rate": 0.08,
        "subtotal": 920.00,
        "total_with_tax": 1000.00,
        "status": "pending_approval",
        "type": "invoice",
        "notes": "Test invoice for unit testing",
        "company_id": str(uuid.uuid4()),
        "created_by_id": str(uuid.uuid4()),
        "posted_to_erp": False,
        "ocr_data": {
            "confidence": 0.95,
            "extracted_fields": {
                "total_amount": 1000.00,
                "supplier_name": "Test Supplier Ltd",
                "invoice_number": "TEST-INV-001"
            }
        },
        "workflow_data": {
            "approval_required": True,
            "auto_approve": False
        }
    }


def get_test_company_data() -> Dict[str, Any]:
    """Get test company data"""
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Company Ltd",
        "display_name": "Test Company",
        "description": "Test company for unit testing",
        "email": "test@company.com",
        "phone": "+1234567890",
        "website": "https://testcompany.com",
        "address_line1": "456 Company Street",
        "city": "Test City",
        "state": "Test State",
        "postal_code": "12345",
        "country": "Test Country",
        "tax_id": "TAX123456789",
        "industry": "Technology",
        "company_size": "51-200",
        "status": "active",
        "tier": "growth",
        "subscription_id": str(uuid.uuid4()),
        "trial_ends_at": None,
        "subscription_ends_at": None,
        "settings": {},
        "features": {},
        "max_users": 10,
        "max_storage_gb": 100,
        "max_invoices_per_month": 1000
    }


def get_test_user_data(company_id: str = None) -> Dict[str, Any]:
    """Get test user data"""
    if company_id is None:
        company_id = str(uuid.uuid4())
    
    return {
        "id": str(uuid.uuid4()),
        "email": "testuser@company.com",
        "username": "testuser",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBdFqN3K.3qHxW",  # "password123"
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "avatar_url": None,
        "company_id": company_id,
        "role": "admin",
        "status": "active",
        "is_email_verified": True,
        "is_2fa_enabled": False,
        "last_login": None,
        "failed_login_attempts": 0,
        "locked_until": None
    }
