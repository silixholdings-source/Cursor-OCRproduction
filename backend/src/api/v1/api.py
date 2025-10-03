from fastapi import APIRouter
from .endpoints import health, auth, invoices, companies, users, erp, processing, ocr, database, analytics, billing, approvals, currency, integrations, azure_auth, stats, contact, erp_automation, system

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(erp.router, prefix="/erp", tags=["erp-integration"])
api_router.include_router(processing.router, prefix="/processing", tags=["invoice-processing"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr-ai-ml"])
api_router.include_router(database.router, prefix="/database", tags=["database-management"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics-bi"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing-subscriptions"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(currency.router, prefix="/currency", tags=["currency"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(azure_auth.router, prefix="/auth", tags=["enterprise-sso"])
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(erp_automation.router, prefix="/erp-automation", tags=["erp-automation"])
api_router.include_router(system.router, prefix="/system", tags=["system-management"])
