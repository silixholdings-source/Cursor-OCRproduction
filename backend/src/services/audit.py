"""
Audit Service for compliance and security tracking
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.models.audit import AuditLog, AuditAction, AuditResourceType
from src.models.user import User
from src.models.company import Company
from src.models.invoice import Invoice
from core.config import settings

logger = logging.getLogger(__name__)

class AuditService:
    """Audit service for tracking system activities and compliance"""
    
    def __init__(self):
        self.risk_levels = {
            "low": ["read", "login", "logout"],
            "medium": ["create", "update", "approve"],
            "high": ["delete", "role_change", "subscription_change"],
            "critical": ["password_change", "sso_config", "admin_action"]
        }
    
    async def log_activity(self, db: Session, action: AuditAction, resource_type: AuditResourceType,
                          resource_id: uuid.UUID, user: User, company_id: uuid.UUID,
                          details: Dict[str, Any] = None, ip_address: str = None,
                          user_agent: str = None, request_method: str = None,
                          request_path: str = None, request_id: str = None) -> AuditLog:
        """Log an audit event"""
        try:
            # Determine risk level
            risk_level = self._determine_risk_level(action)
            
            # Determine data classification
            data_classification = self._determine_data_classification(resource_type, action)
            
            # Create audit log entry
            audit_log = AuditLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user.id if user else None,
                company_id=company_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                request_id=request_id,
                risk_level=risk_level,
                data_classification=data_classification
            )
            
            # Add compliance tags based on action and resource
            self._add_compliance_tags(audit_log, action, resource_type)
            
            # Save to database
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            logger.info(f"Audit log created: {action.value} on {resource_type.value}:{resource_id}")
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            db.rollback()
            raise
    
    def _determine_risk_level(self, action: AuditAction) -> str:
        """Determine risk level based on action"""
        for level, actions in self.risk_levels.items():
            if action.value in actions:
                return level
        return "low"  # Default to low risk
    
    def _determine_data_classification(self, resource_type: AuditResourceType, action: AuditAction) -> str:
        """Determine data classification based on resource type and action"""
        # High sensitivity resources
        if resource_type in [AuditResourceType.USER, AuditResourceType.COMPANY]:
            if action in [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]:
                return "confidential"
            else:
                return "internal"
        
        # Medium sensitivity resources
        elif resource_type in [AuditResourceType.INVOICE, AuditResourceType.APPROVAL]:
            if action in [AuditAction.APPROVE, AuditAction.REJECT, AuditAction.DELETE]:
                return "confidential"
            else:
                return "internal"
        
        # Low sensitivity resources
        else:
            return "public"
    
    def _add_compliance_tags(self, audit_log: AuditLog, action: AuditAction, resource_type: AuditResourceType):
        """Add compliance tags based on action and resource type"""
        tags = []
        
        # GDPR compliance tags
        if resource_type == AuditResourceType.USER and action in [AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE]:
            tags.extend(["gdpr", "personal_data"])
        
        # SOX compliance tags
        if resource_type == AuditResourceType.INVOICE and action in [AuditAction.APPROVE, AuditAction.REJECT, AuditAction.POST]:
            tags.extend(["sox", "financial_control"])
        
        # SOC2 compliance tags
        if action in [AuditAction.LOGIN, AuditAction.LOGOUT, AuditAction.ROLE_CHANGE]:
            tags.extend(["soc2", "access_control"])
        
        # Add tags to audit log
        for tag in tags:
            audit_log.add_compliance_tag(tag)
    
    async def get_audit_trail(self, db: Session, company_id: uuid.UUID,
                             resource_type: AuditResourceType = None,
                             resource_id: uuid.UUID = None,
                             user_id: uuid.UUID = None,
                             action: AuditAction = None,
                             start_date: datetime = None,
                             end_date: datetime = None,
                             risk_level: str = None,
                             limit: int = 100,
                             offset: int = 0) -> List[AuditLog]:
        """Get audit trail with filtering options"""
        query = db.query(AuditLog).filter(AuditLog.company_id == company_id)
        
        # Apply filters
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        if risk_level:
            query = query.filter(AuditLog.risk_level == risk_level)
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()
    
    async def get_user_activity_summary(self, db: Session, user_id: uuid.UUID,
                                      company_id: uuid.UUID,
                                      days: int = 30) -> Dict[str, Any]:
        """Get summary of user activity for specified period"""
        start_date = datetime.now(UTC) - timedelta(days=days)
        
        # Get user's audit logs
        audit_logs = await self.get_audit_trail(
            db, company_id, user_id=user_id, start_date=start_date
        )
        
        # Calculate activity metrics
        total_actions = len(audit_logs)
        action_counts = {}
        resource_counts = {}
        risk_level_counts = {}
        
        for log in audit_logs:
            # Count actions
            action = log.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
            
            # Count resources
            resource = log.resource_type.value
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
            
            # Count risk levels
            risk = log.risk_level or "unknown"
            risk_level_counts[risk] = risk_level_counts.get(risk, 0) + 1
        
        return {
            "user_id": str(user_id),
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.now(UTC).isoformat(),
            "total_actions": total_actions,
            "action_breakdown": action_counts,
            "resource_breakdown": resource_counts,
            "risk_level_breakdown": risk_level_counts,
            "average_actions_per_day": total_actions / days if days > 0 else 0
        }
    
    async def get_compliance_report(self, db: Session, company_id: uuid.UUID,
                                  start_date: datetime = None,
                                  end_date: datetime = None) -> Dict[str, Any]:
        """Generate compliance report for company"""
        if not start_date:
            start_date = datetime.now(UTC) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(UTC)
        
        # Get all audit logs for period
        audit_logs = await self.get_audit_trail(
            db, company_id, start_date=start_date, end_date=end_date
        )
        
        # Compliance metrics
        gdpr_events = [log for log in audit_logs if "gdpr" in log.compliance_tags]
        sox_events = [log for log in audit_logs if "sox" in log.compliance_tags]
        soc2_events = [log for log in audit_logs if "soc2" in log.compliance_tags]
        
        # Risk analysis
        high_risk_events = [log for log in audit_logs if log.risk_level in ["high", "critical"]]
        
        # Data access patterns
        data_access_events = [log for log in audit_logs if log.data_classification in ["confidential", "restricted"]]
        
        return {
            "company_id": str(company_id),
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_events": len(audit_logs),
            "compliance_metrics": {
                "gdpr_events": len(gdpr_events),
                "sox_events": len(sox_events),
                "soc2_events": len(soc2_events)
            },
            "risk_analysis": {
                "high_risk_events": len(high_risk_events),
                "risk_distribution": {
                    "low": len([log for log in audit_logs if log.risk_level == "low"]),
                    "medium": len([log for log in audit_logs if log.risk_level == "medium"]),
                    "high": len([log for log in audit_logs if log.risk_level == "high"]),
                    "critical": len([log for log in audit_logs if log.risk_level == "critical"])
                }
            },
            "data_protection": {
                "confidential_data_access": len([log for log in data_access_events if log.data_classification == "confidential"]),
                "restricted_data_access": len([log for log in data_access_events if log.data_classification == "restricted"])
            },
            "recommendations": self._generate_compliance_recommendations(audit_logs)
        }
    
    def _generate_compliance_recommendations(self, audit_logs: List[AuditLog]) -> List[str]:
        """Generate compliance recommendations based on audit data"""
        recommendations = []
        
        # Check for unusual patterns
        high_risk_count = len([log for log in audit_logs if log.risk_level in ["high", "critical"]])
        if high_risk_count > len(audit_logs) * 0.1:  # More than 10% high risk
            recommendations.append("High proportion of high-risk activities detected. Review access controls and user permissions.")
        
        # Check for data access patterns
        confidential_access = [log for log in audit_logs if log.data_classification == "confidential"]
        if len(confidential_access) > len(audit_logs) * 0.3:  # More than 30% confidential access
            recommendations.append("High volume of confidential data access. Implement additional access controls and monitoring.")
        
        # Check for compliance gaps
        gdpr_events = [log for log in audit_logs if "gdpr" in log.compliance_tags]
        if not gdpr_events:
            recommendations.append("No GDPR-related activities detected. Ensure GDPR compliance procedures are in place.")
        
        return recommendations
    
    async def export_audit_logs(self, db: Session, company_id: uuid.UUID,
                               start_date: datetime = None,
                               end_date: datetime = None,
                               format: str = "json") -> str:
        """Export audit logs in specified format"""
        audit_logs = await self.get_audit_trail(
            db, company_id, start_date=start_date, end_date=end_date
        )
        
        if format.lower() == "json":
            return self._export_to_json(audit_logs)
        elif format.lower() == "csv":
            return self._export_to_csv(audit_logs)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_to_json(self, audit_logs: List[AuditLog]) -> str:
        """Export audit logs to JSON format"""
        import json
        
        export_data = []
        for log in audit_logs:
            export_data.append({
                "id": str(log.id),
                "action": log.action.value,
                "resource_type": log.resource_type.value,
                "resource_id": str(log.resource_id),
                "user_id": str(log.user_id) if log.user_id else None,
                "company_id": str(log.company_id),
                "timestamp": log.timestamp.isoformat(),
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "request_method": log.request_method,
                "request_path": log.request_path,
                "risk_level": log.risk_level,
                "data_classification": log.data_classification,
                "compliance_tags": log.compliance_tags,
                "details": log.details
            })
        
        return json.dumps(export_data, indent=2)
    
    def _export_to_csv(self, audit_logs: List[AuditLog]) -> str:
        """Export audit logs to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Action", "Resource Type", "Resource ID", "User ID", "Company ID",
            "Timestamp", "IP Address", "User Agent", "Request Method", "Request Path",
            "Risk Level", "Data Classification", "Compliance Tags", "Details"
        ])
        
        # Write data
        for log in audit_logs:
            writer.writerow([
                str(log.id),
                log.action.value,
                log.resource_type.value,
                str(log.resource_id),
                str(log.user_id) if log.user_id else "",
                str(log.company_id),
                log.timestamp.isoformat(),
                log.ip_address or "",
                log.user_agent or "",
                log.request_method or "",
                log.request_path or "",
                log.risk_level or "",
                log.data_classification or "",
                ",".join(log.compliance_tags),
                str(log.details)
            ])
        
        return output.getvalue()
    
    async def cleanup_old_logs(self, db: Session, company_id: uuid.UUID,
                              retention_days: int = 2555) -> int:
        """Clean up old audit logs based on retention policy (default: 7 years)"""
        cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
        
        # Count logs to be deleted
        count = db.query(AuditLog).filter(
            and_(
                AuditLog.company_id == company_id,
                AuditLog.timestamp < cutoff_date
            )
        ).count()
        
        # Delete old logs
        deleted = db.query(AuditLog).filter(
            and_(
                AuditLog.company_id == company_id,
                AuditLog.timestamp < cutoff_date
            )
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted} old audit logs for company {company_id}")
        return deleted
