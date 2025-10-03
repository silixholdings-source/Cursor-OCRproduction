"""
Integration Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta

from core.database import get_db
from core.auth import auth_manager
from src.models.user import User, UserRole
from services.erp import ERPIntegrationService

router = APIRouter()

# Initialize ERP integration service
erp_service = ERPIntegrationService()

@router.get("/dashboard-data")
async def get_integration_dashboard_data(
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Get integration dashboard data"""
    try:
        # Get health status of all ERP systems
        health_status = await erp_service.health_check_all()
        
        # Transform to dashboard format
        integrations = []
        total_syncs = 0
        successful_syncs = 0
        
        for erp_type, status in health_status.items():
            if erp_type == "mock":
                continue
                
            # Mock sync data (in production this would come from database)
            sync_count = 100 + (hash(erp_type) % 500)
            success_rate = 95 + (hash(erp_type) % 5)
            
            integrations.append({
                "id": erp_type,
                "name": erp_type.replace("_", " ").title(),
                "type": "ERP",
                "status": "active" if status.get("status") == "healthy" else "error",
                "lastSync": status.get("timestamp"),
                "nextSync": datetime.now(UTC).isoformat(),
                "successRate": success_rate,
                "totalSyncs": sync_count,
                "failedSyncs": sync_count - int(sync_count * success_rate / 100),
                "avgResponseTime": 2.5 + (hash(erp_type) % 3),
                "config": {
                    "endpoint": f"https://api.{erp_type}.com/v1.0",
                    "version": "1.0",
                    "authType": "OAuth2",
                    "timeout": 30
                }
            })
            
            total_syncs += sync_count
            successful_syncs += int(sync_count * success_rate / 100)
        
        # Calculate metrics
        metrics = {
            "totalIntegrations": len(integrations),
            "activeIntegrations": len([i for i in integrations if i["status"] == "active"]),
            "totalSyncs": total_syncs,
            "successfulSyncs": successful_syncs,
            "failedSyncs": total_syncs - successful_syncs,
            "avgResponseTime": sum(i["avgResponseTime"] for i in integrations) / len(integrations) if integrations else 0,
            "dataVolume": total_syncs * 1.5  # MB
        }
        
        return {
            "integrations": integrations,
            "metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration dashboard data: {str(e)}"
        )

@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger sync for a specific integration"""
    try:
        # Validate user has permission
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to sync integrations"
            )
        
        # Get the adapter (reuse ERP service)
        adapter = erp_service.get_adapter(integration_id)
        
        # Validate connection first
        connection_status = await adapter.validate_connection()
        if connection_status["status"] != "connected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Integration connection failed: {connection_status.get('message', 'Unknown error')}"
            )
        
        # Mock sync result (in production this would do actual sync)
        return {
            "status": "success",
            "message": f"Sync completed for {integration_id}",
            "recordsSynced": 25,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync integration: {str(e)}"
        )

@router.post("/{integration_id}/toggle")
async def toggle_integration(
    integration_id: str,
    toggle_data: Dict[str, Any],
    current_user: User = Depends(auth_manager.get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle integration status (enable/disable)"""
    try:
        # Validate user has permission
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, UserRole.OWNER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to toggle integrations"
            )
        
        new_status = toggle_data.get("status", "active")
        
        # In production, this would update the integration status in database
        return {
            "status": "success",
            "message": f"Integration {integration_id} {new_status}",
            "integration_id": integration_id,
            "new_status": new_status,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle integration: {str(e)}"
        )


