# Services package
# Import only the working services to avoid import issues
from .simple_ocr import SimpleOCRService

# Try to import other services, but don't fail if they have issues
try:
    from .ocr import OCRService
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False

try:
    from .erp import (
        ERPAdapter, 
        MockERPAdapter, 
        MicrosoftDynamicsGPAdapter, 
        Dynamics365BCAdapter, 
        XeroAdapter,
        QuickBooksAdapter,
        SageAdapter,
        SAPAdapter,
        ERPIntegrationService
    )
    _ERP_AVAILABLE = True
except ImportError:
    _ERP_AVAILABLE = False

try:
    from .workflow import WorkflowEngine
    _WORKFLOW_AVAILABLE = True
except ImportError:
    _WORKFLOW_AVAILABLE = False

try:
    from .billing import StripeService
    _BILLING_AVAILABLE = True
except ImportError:
    _BILLING_AVAILABLE = False

try:
    from .audit import AuditService
    _AUDIT_AVAILABLE = True
except ImportError:
    _AUDIT_AVAILABLE = False

# Always available
__all__ = ["SimpleOCRService"]

# Conditionally add available services
if _OCR_AVAILABLE:
    __all__.append("OCRService")
if _ERP_AVAILABLE:
    __all__.extend([
        "ERPAdapter", "MockERPAdapter", "MicrosoftDynamicsGPAdapter", 
        "Dynamics365BCAdapter", "XeroAdapter", "QuickBooksAdapter",
        "SageAdapter", "SAPAdapter", "ERPIntegrationService"
    ])
if _WORKFLOW_AVAILABLE:
    __all__.append("WorkflowEngine")
if _BILLING_AVAILABLE:
    __all__.append("StripeService")
if _AUDIT_AVAILABLE:
    __all__.append("AuditService")
