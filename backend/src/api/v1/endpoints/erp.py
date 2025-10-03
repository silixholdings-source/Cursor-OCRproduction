"""
ERP Integration Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User, UserRole
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from services.erp import ERPIntegrationService, ERPAdapter
from schemas.erp import (
    ERPConnectionRequest,
    ERPConnectionResponse,
    ERPHealthResponse,
    ERPPostingRequest,
    ERPPostingResponse,
    ERPStatusResponse,
    ERPConfigurationSchema,
    ERPValidationResult,
    ERPConnectionInfo,
    ERPCapabilities,
    ERPBatchPostingRequest,
    ERPBatchPostingResponse,
    ERPAuditLog,
    ERPMetrics,
    ERPSyncRequest,
    ERPSyncResponse,
    ERPType,
    ERPConnectionStatus,
    ERPPostingMethod
)

router = APIRouter()

# Initialize ERP integration service
erp_service = ERPIntegrationService()

@router.post("/register", response_model=ERPConnectionResponse)
async def register_erp_integration(
    request: ERPConnectionRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Register ERP integration for a company"""
    try:
        # Validate user has permission to manage ERP integrations
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage ERP integrations"
            )
        
        # Register ERP integration
        result = await erp_service.register_erp_connection(
            company_id=str(current_user.company_id),
            erp_type=request.erp_type.value,
            connection_config=request.configuration
        )
        
        if result["status"] == "success":
            # Create audit log
            audit_log = AuditLog(
                company_id=current_user.company_id,
                user_id=current_user.id,
                action=AuditAction.CREATE,
                resource_type=AuditResourceType.ERP_CONNECTION,
                resource_id=f"erp_{request.erp_type.value}",
                details={
                    "erp_type": request.erp_type.value,
                    "connection_name": request.connection_name
                }
            )
            db.add(audit_log)
            db.commit()
            
            return ERPConnectionResponse(
                status="success",
                message=result["message"],
                erp_type=result["erp_type"],
                company_id=result["company_id"],
                connection_id=str(uuid.uuid4()),
                validated_at=datetime.now(UTC)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register ERP integration: {str(e)}"
        )


@router.get("/health/{erp_type}", response_model=ERPHealthResponse)
async def check_erp_health(
    erp_type: ERPType,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Check ERP system health"""
    try:
        adapter = erp_service.get_adapter(erp_type.value)
        health_result = await adapter.health_check()
        
        return ERPHealthResponse(
            erp_type=erp_type.value,
            status=health_result.get("status", "unknown"),
            timestamp=datetime.now(UTC),
            version=health_result.get("version"),
            company_id=health_result.get("company_id"),
            error=health_result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check ERP health: {str(e)}"
        )


@router.post("/post-invoice", response_model=ERPPostingResponse)
async def post_invoice_to_erp(
    request: ERPPostingRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Post invoice to ERP system"""
    try:
        # Get invoice from database
        from src.models.invoice import Invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == request.invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Post to ERP
        if request.posting_method == ERPPostingMethod.WITH_PO and request.po_number:
            adapter = erp_service.get_adapter(request.erp_type.value)
            result = await adapter.process_invoice_with_po(
                invoice, request.po_number, request.company_settings
            )
        elif request.posting_method == ERPPostingMethod.WITHOUT_PO:
            adapter = erp_service.get_adapter(request.erp_type.value)
            result = await adapter.process_invoice_without_po(
                invoice, request.company_settings
            )
        else:
            result = await erp_service.post_invoice(
                invoice, request.erp_type.value, request.company_settings
            )
        
        # Create audit log
        audit_log = AuditLog(
            company_id=current_user.company_id,
            user_id=current_user.id,
            action=AuditAction.UPDATE,
            resource_type=AuditResourceType.INVOICE,
            resource_id=invoice.id,
            details={
                "erp_type": request.erp_type.value,
                "posting_method": request.posting_method.value,
                "erp_doc_id": result.get("erp_doc_id"),
                "status": result.get("status")
            }
        )
        db.add(audit_log)
        db.commit()
        
        return ERPPostingResponse(
            status=result.get("status", "error"),
            erp_doc_id=result.get("erp_doc_id"),
            erp_name=result.get("erp_name", request.erp_type.value),
            processing_type=result.get("processing_type"),
            method=result.get("method"),
            timestamp=datetime.now(UTC),
            message=result.get("message", "Invoice posting completed"),
            error=result.get("error"),
            posted_at=datetime.now(UTC) if result.get("status") == "success" else None,
            erp_data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post invoice to ERP: {str(e)}"
        )


@router.get("/invoice-status/{erp_doc_id}", response_model=ERPStatusResponse)
async def get_invoice_status(
    erp_doc_id: str,
    erp_type: ERPType,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice status from ERP system"""
    try:
        adapter = erp_service.get_adapter(erp_type.value)
        status_result = await adapter.get_invoice_status(erp_doc_id)
        
        return ERPStatusResponse(
            status=status_result.get("status", "unknown"),
            erp_doc_id=erp_doc_id,
            erp_name=status_result.get("erp_name", erp_type.value),
            posted_at=status_result.get("posted_at"),
            last_updated=datetime.now(UTC),
            error=status_result.get("error"),
            erp_data=status_result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get invoice status: {str(e)}"
        )


@router.post("/validate-config", response_model=ERPValidationResult)
async def validate_erp_configuration(
    config: ERPConfigurationSchema,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Validate ERP configuration"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to validate ERP configurations"
            )
        
        # Validate configuration
        result = await erp_service.validate_erp_configuration(
            erp_type=config.erp_type.value,
            company_settings=config.configuration
        )
        
        return ERPValidationResult(
            status=result.get("status", "error"),
            erp_type=config.erp_type,
            connection_result=result.get("connection"),
            test_posting=result.get("test_posting"),
            validated_at=datetime.now(UTC),
            error=result.get("error"),
            warnings=result.get("warnings", []),
            recommendations=result.get("recommendations", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate ERP configuration: {str(e)}"
        )


@router.get("/capabilities/{erp_type}", response_model=ERPCapabilities)
async def get_erp_capabilities(
    erp_type: ERPType,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get ERP system capabilities"""
    try:
        adapter = erp_service.get_adapter(erp_type.value)
        
        return ERPCapabilities(
            erp_type=erp_type,
            supports_po_matching=adapter.supports_po_matching(),
            supports_no_po_processing=adapter.supports_no_po_processing(),
            supported_invoice_types=adapter.get_supported_invoice_types(),
            api_version="1.0",
            max_file_size=10485760,  # 10MB
            supported_formats=["pdf", "jpg", "jpeg", "png", "tiff"],
            real_time_posting=True,
            batch_posting=True,
            custom_fields=True,
            multi_currency=True,
            tax_handling="advanced"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ERP capabilities: {str(e)}"
        )


@router.get("/connections", response_model=List[ERPConnectionInfo])
async def list_erp_connections(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """List all ERP connections for the company"""
    try:
        # This would typically come from a database
        # For now, return available adapters
        connections = []
        for erp_type, adapter in erp_service.adapters.items():
            if erp_type != "mock":  # Skip mock adapter
                connections.append(ERPConnectionInfo(
                    connection_id=str(uuid.uuid4()),
                    erp_type=ERPType(erp_type),
                    connection_name=f"{erp_type.title()} Connection",
                    status=ERPConnectionStatus.CONNECTED,
                    created_at=datetime.now(UTC),
                    last_used=datetime.now(UTC),
                    last_health_check=datetime.now(UTC),
                    health_status="healthy",
                    configuration_summary={"base_url": "configured"},
                    usage_count=0
                ))
        
        return connections
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list ERP connections: {str(e)}"
        )


@router.post("/batch-post", response_model=ERPBatchPostingResponse)
async def batch_post_invoices(
    request: ERPBatchPostingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Post multiple invoices to ERP system in batch"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for batch operations"
            )
        
        batch_id = str(uuid.uuid4())
        
        # Start background task for batch processing
        background_tasks.add_task(
            process_batch_posting,
            batch_id,
            request,
            current_user.company_id,
            current_user.id
        )
        
        return ERPBatchPostingResponse(
            batch_id=batch_id,
            status="pending",
            total_invoices=len(request.invoice_ids),
            processed_count=0,
            success_count=0,
            error_count=0,
            created_at=datetime.now(UTC),
            erp_type=request.erp_type,
            results=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start batch posting: {str(e)}"
        )


@router.get("/metrics/{erp_type}", response_model=ERPMetrics)
async def get_erp_metrics(
    erp_type: ERPType,
    period_days: int = 30,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get ERP performance and usage metrics"""
    try:
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view metrics"
            )
        
        # This would typically query actual metrics from database
        # For now, return mock metrics
        return ERPMetrics(
            erp_type=erp_type,
            company_id=str(current_user.company_id),
            period_start=datetime.now(UTC),
            period_end=datetime.now(UTC),
            total_postings=150,
            successful_postings=145,
            failed_postings=5,
            avg_posting_time_ms=1250.5,
            error_rate=3.33,
            common_errors=[
                {"error": "Connection timeout", "count": 3},
                {"error": "Invalid vendor", "count": 2}
            ],
            uptime_percentage=99.5,
            avg_response_time_ms=850.0,
            max_response_time_ms=5000.0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ERP metrics: {str(e)}"
        )


async def process_batch_posting(
    batch_id: str,
    request: ERPBatchPostingRequest,
    company_id: str,
    user_id: str
):
    """Background task for processing batch invoice posting"""
    try:
        # This would implement the actual batch processing logic
        # For now, just log the task
        print(f"Processing batch {batch_id} with {len(request.invoice_ids)} invoices")
        
        # Simulate processing delay
        import asyncio
        await asyncio.sleep(1)
        
        # Update batch status in database
        # This would typically update a batch status table
        
    except Exception as e:
        print(f"Batch processing error: {e}")
        # Log error and update batch status

@router.get("/integrations", response_model=Dict[str, Any])
async def get_erp_integrations(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get available ERP integrations"""
    try:
        available_erps = {}
        for erp_type in ERPType:
            if erp_type != ERPType.MOCK:
                adapter = erp_service.get_adapter(erp_type.value)
                available_erps[erp_type.value] = {
                    "name": erp_type.value.replace("_", " ").title(),
                    "capabilities": {
                        "supports_po_matching": adapter.supports_po_matching(),
                        "supports_no_po_processing": adapter.supports_no_po_processing(),
                        "supported_invoice_types": adapter.get_supported_invoice_types()
                    },
                    "status": "available"
                }
        
        return {
            "available_erps": available_erps,
            "total_count": len(available_erps),
            "company_id": str(current_user.company_id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ERP integrations: {str(e)}"
        )

@router.post("/integrations/{integration_id}/sync")
async def sync_erp_integration(
    integration_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger sync for a specific ERP integration"""
    try:
        # Validate user has permission
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to sync ERP integrations"
            )
        
        # Get the adapter
        adapter = erp_service.get_adapter(integration_id)
        
        # Validate connection first
        connection_status = await adapter.validate_connection()
        if connection_status["status"] != "connected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ERP connection failed: {connection_status.get('message', 'Unknown error')}"
            )
        
        # In a real implementation, this would:
        # 1. Fetch pending invoices from database
        # 2. Sync them to the ERP system
        # 3. Update sync status in database
        # 4. Return actual sync results
        
        # For now, return success with mock data
        return {
            "status": "success",
            "message": f"Sync completed for {integration_id}",
            "recordsSynced": 15,  # This would be actual count
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync ERP integration: {str(e)}"
        )

@router.get("/health", response_model=ERPHealthResponse)
async def check_erp_health(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Check health of company's ERP integration"""
    try:
        company_id = str(current_user.company_id)
        
        # Perform health check
        health_results = await erp_service.health_check_all()
        company_health = health_results.get("mock", {})
        
        return ERPHealthResponse(
            status=company_health.get("status", "unknown"),
            message=f"ERP health check completed for mock ERP",
            erp_type="mock",
            last_check=company_health.get("timestamp"),
            details=company_health
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check ERP health: {str(e)}"
        )

@router.post("/post-invoice", response_model=ERPPostingResponse)
async def post_invoice_to_erp(
    request: ERPPostingRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Post invoice to ERP system"""
    try:
        # Validate user has permission to post invoices
        if current_user.role not in ["admin", "manager", "approver"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to post invoices to ERP"
            )
        
        # Get invoice from database
        from src.models.invoice import Invoice
        invoice = db.query(Invoice).filter(
            Invoice.id == request.invoice_id,
            Invoice.company_id == current_user.company_id
        ).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Check if invoice is approved
        if invoice.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice must be approved before posting to ERP"
            )
        
        # Get company settings
        company_settings = {
            "erp_type": "dynamics_gp",  # This would come from company config
            "company_id": str(current_user.company_id),
            "default_currency": "USD",
            "tax_calculation": "automatic"
        }
        
        # Post to ERP
        result = await erp_service.post_invoice(
            invoice=invoice,
            erp_type="mock",
            company_settings=company_settings
        )
        
        if result["status"] == "success":
            # Update invoice status
            invoice.status = "posted_to_erp"
            invoice.erp_document_id = result["erp_doc_id"]
            invoice.posted_to_erp = True
            invoice.erp_posting_date = datetime.now(UTC)
            db.commit()
            
            return ERPPostingResponse(
                status="success",
                message="Invoice successfully posted to ERP",
                erp_doc_id=result["erp_doc_id"],
                invoice_id=str(invoice.id),
                posted_at=invoice.erp_posting_date.isoformat()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post invoice to ERP: {str(e)}"
        )

@router.get("/status/{erp_document_id}")
async def get_erp_invoice_status(
    erp_document_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get invoice status from ERP system"""
    try:
        # Get status from ERP
        status_result = await erp_service.check_invoice_status(erp_document_id, "mock")
        
        return {
            "status": "success",
            "erp_document_id": erp_document_id,
            "erp_status": status_result.get("status"),
            "posted_at": status_result.get("posted_at"),
            "erp_name": status_result.get("erp_name"),
            "details": status_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ERP invoice status: {str(e)}"
        )

@router.get("/connections")
async def list_erp_connections(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """List ERP connections for the company"""
    try:
        # Only admins can view ERP connections
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view ERP connections"
            )
        
        # Simplified connections list
        connections = [{"erp_type": "mock", "company_id": str(current_user.company_id), "status": "active"}]
        company_connections = connections
        
        return {
            "status": "success",
            "connections": company_connections,
            "total": len(company_connections)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list ERP connections: {str(e)}"
        )

@router.delete("/connections/{erp_type}")
async def remove_erp_connection(
    erp_type: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Remove ERP integration for a company"""
    try:
        # Only admins can remove ERP connections
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can remove ERP connections"
            )
        
        company_id = str(current_user.company_id)
        
        # Simplified removal (mock implementation)
        # In a real implementation, this would remove from database
        
        return {
            "status": "success",
            "message": f"ERP connection {erp_type} removed successfully",
            "erp_type": erp_type,
            "company_id": company_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove ERP connection: {str(e)}"
        )

@router.post("/test-connection")
async def test_erp_connection(
    request: ERPConnectionRequest,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Test ERP connection without registering it"""
    try:
        # Validate user has permission to test ERP connections
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to test ERP connections"
            )
        
        # Test connection using the service
        try:
            validation_result = await erp_service.validate_erp_configuration(
                request.erp_type,
                request.connection_config
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        if validation_result["status"] in ["valid", "success"]:
            return {
                "status": "success",
                "message": "ERP connection test successful",
                "erp_type": request.erp_type,
                "details": validation_result
            }
        else:
            return {
                "status": "error",
                "message": "ERP connection test failed",
                "erp_type": request.erp_type,
                "details": validation_result
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test ERP connection: {str(e)}"
        )












