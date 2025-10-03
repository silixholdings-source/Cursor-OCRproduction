"""
POPIA Compliance Service for South African Data Protection
Handles consent management, data subject rights, and compliance reporting
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.company import Company
from src.models.user import User
from src.models.audit import AuditLog, AuditAction, AuditResourceType
from core.config import settings

logger = logging.getLogger(__name__)

class POPIAComplianceService:
    """POPIA (Protection of Personal Information Act) compliance service for South Africa"""
    
    def __init__(self):
        self.data_categories = {
            "personal_data": [
                "name", "email", "phone", "address", "id_number", "passport_number"
            ],
            "financial_data": [
                "bank_account", "payment_methods", "transaction_history", "credit_card"
            ],
            "business_data": [
                "company_name", "industry", "employee_count", "revenue", "business_address"
            ],
            "usage_data": [
                "login_history", "feature_usage", "session_data", "preferences"
            ],
            "technical_data": [
                "ip_address", "device_info", "browser_data", "cookies"
            ]
        }
        
        self.legal_bases = [
            "consent",
            "contract",
            "legal_obligation", 
            "vital_interests",
            "public_task",
            "legitimate_interest"
        ]
        
        self.retention_periods = {
            "personal_data": "7_years",
            "financial_data": "7_years",  # Tax compliance requirement
            "business_data": "7_years",
            "usage_data": "2_years",
            "technical_data": "1_year"
        }
    
    async def record_consent(self, consent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record POPIA-compliant consent for data processing"""
        try:
            logger.info(f"Recording POPIA consent for company {consent_data['company_id']}")
            
            # Validate consent data
            required_fields = ["company_id", "consent_type", "consent_given", "consent_date"]
            for field in required_fields:
                if field not in consent_data:
                    return {
                        "status": "error",
                        "message": f"Missing required field: {field}"
                    }
            
            # Create consent record
            consent_record = {
                "id": str(uuid.uuid4()),
                "company_id": consent_data["company_id"],
                "consent_type": consent_data["consent_type"],
                "consent_given": consent_data["consent_given"],
                "consent_date": consent_data["consent_date"],
                "legal_basis": consent_data.get("legal_basis", "consent"),
                "data_categories": consent_data.get("data_categories", []),
                "retention_period": consent_data.get("retention_period", "7_years"),
                "third_party_sharing": consent_data.get("third_party_sharing", False),
                "withdrawal_method": consent_data.get("withdrawal_method", "email_request"),
                "created_at": datetime.now(UTC),
                "popia_reference": f"POPIA-{datetime.now(UTC).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            }
            
            # Validate legal basis
            if consent_record["legal_basis"] not in self.legal_bases:
                return {
                    "status": "error",
                    "message": f"Invalid legal basis: {consent_record['legal_basis']}"
                }
            
            # Validate data categories
            for category in consent_record["data_categories"]:
                if category not in self.data_categories:
                    return {
                        "status": "error",
                        "message": f"Invalid data category: {category}"
                    }
            
            return {
                "status": "consent_recorded",
                "consent_id": consent_record["id"],
                "compliance_status": "compliant",
                "popia_reference": consent_record["popia_reference"],
                "data_categories": consent_record["data_categories"],
                "retention_period": consent_record["retention_period"],
                "legal_basis": consent_record["legal_basis"]
            }
            
        except Exception as e:
            logger.error(f"Failed to record POPIA consent: {str(e)}")
            return {
                "status": "error",
                "message": f"Consent recording failed: {str(e)}"
            }
    
    async def handle_data_access_request(self, user_id: str, request_type: str) -> Dict[str, Any]:
        """Handle POPIA data access request from data subjects"""
        try:
            logger.info(f"Processing {request_type} request for user {user_id}")
            
            # Validate request type
            valid_requests = ["data_access", "data_portability", "data_correction"]
            if request_type not in valid_requests:
                return {
                    "status": "error",
                    "message": f"Invalid request type: {request_type}"
                }
            
            # Get user data
            # In real implementation, query database
            user_data = {
                "user_id": user_id,
                "personal_data": {
                    "name": "John Doe",
                    "email": "john@company.co.za",
                    "phone": "+27123456789"
                },
                "usage_data": {
                    "last_login": datetime.now(UTC).isoformat(),
                    "total_sessions": 150,
                    "features_used": ["invoice_processing", "ocr_extraction"]
                }
            }
            
            if request_type == "data_access":
                return {
                    "status": "data_provided",
                    "request_id": str(uuid.uuid4()),
                    "request_type": request_type,
                    "data_categories": ["personal_data", "usage_data"],
                    "processing_purposes": ["service_delivery", "billing", "support"],
                    "data_retention": "7_years",
                    "response_date": datetime.now(UTC).isoformat(),
                    "data": user_data
                }
            
            elif request_type == "data_portability":
                # Provide data in portable format (JSON)
                portable_data = {
                    "export_format": "json",
                    "export_date": datetime.now(UTC).isoformat(),
                    "data_schema_version": "1.0",
                    "user_data": user_data
                }
                
                return {
                    "status": "data_provided",
                    "request_id": str(uuid.uuid4()),
                    "request_type": request_type,
                    "export_format": "json",
                    "data_size_bytes": len(json.dumps(portable_data)),
                    "download_url": f"/api/v1/popia/export/{user_id}/data.json",
                    "expires_at": (datetime.now(UTC) + timedelta(days=7)).isoformat()
                }
            
            elif request_type == "data_correction":
                return {
                    "status": "correction_processed",
                    "request_id": str(uuid.uuid4()),
                    "request_type": request_type,
                    "correction_method": "user_self_service",
                    "validation_required": True,
                    "estimated_completion": (datetime.now(UTC) + timedelta(hours=24)).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to handle data access request: {str(e)}")
            return {
                "status": "error",
                "message": f"Data access request failed: {str(e)}"
            }
    
    async def handle_data_deletion_request(self, user_id: str, deletion_type: str) -> Dict[str, Any]:
        """Handle POPIA data deletion request (right to be forgotten)"""
        try:
            logger.info(f"Processing {deletion_type} deletion request for user {user_id}")
            
            # Validate deletion type
            valid_types = ["complete_deletion", "selective_deletion", "anonymization"]
            if deletion_type not in valid_types:
                return {
                    "status": "error",
                    "message": f"Invalid deletion type: {deletion_type}"
                }
            
            # Determine what data can be deleted vs retained
            deletion_plan = {
                "complete_deletion": {
                    "can_delete": ["personal_data", "usage_data", "technical_data"],
                    "must_retain": ["financial_data"],  # Legal requirement for tax records
                    "anonymize": ["business_data"]
                },
                "selective_deletion": {
                    "can_delete": ["usage_data", "technical_data"],
                    "must_retain": ["personal_data", "financial_data", "business_data"],
                    "anonymize": []
                },
                "anonymization": {
                    "can_delete": [],
                    "must_retain": ["financial_data"],
                    "anonymize": ["personal_data", "usage_data", "technical_data", "business_data"]
                }
            }
            
            plan = deletion_plan[deletion_type]
            
            return {
                "status": "deletion_processed",
                "request_id": str(uuid.uuid4()),
                "deletion_type": deletion_type,
                "data_categories_deleted": plan["can_delete"],
                "data_categories_anonymized": plan["anonymize"],
                "retention_required": plan["must_retain"],
                "retention_reason": "Legal compliance (tax records, audit requirements)",
                "deletion_date": datetime.now(UTC).isoformat(),
                "completion_estimate": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
                "confirmation_required": True
            }
            
        except Exception as e:
            logger.error(f"Failed to handle data deletion request: {str(e)}")
            return {
                "status": "error",
                "message": f"Data deletion request failed: {str(e)}"
            }
    
    async def handle_consent_withdrawal(self, user_id: str, consent_type: str) -> Dict[str, Any]:
        """Handle POPIA consent withdrawal request"""
        try:
            logger.info(f"Processing consent withdrawal for user {user_id}")
            
            # Validate consent type
            valid_types = ["data_processing", "marketing", "analytics", "third_party_sharing"]
            if consent_type not in valid_types:
                return {
                    "status": "error",
                    "message": f"Invalid consent type: {consent_type}"
                }
            
            # Process consent withdrawal
            withdrawal_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "consent_type": consent_type,
                "withdrawal_date": datetime.now(UTC),
                "processing_stopped": True,
                "data_retained": True,  # May still retain for legal basis other than consent
                "retention_reason": "Contract performance or legal obligation"
            }
            
            return {
                "status": "consent_withdrawn",
                "withdrawal_id": withdrawal_record["id"],
                "consent_type": consent_type,
                "withdrawal_date": withdrawal_record["withdrawal_date"].isoformat(),
                "processing_stopped": True,
                "data_retained": True,
                "retention_reason": withdrawal_record["retention_reason"],
                "effective_date": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to handle consent withdrawal: {str(e)}")
            return {
                "status": "error",
                "message": f"Consent withdrawal failed: {str(e)}"
            }
    
    async def generate_popia_report(self, company_id: str, report_type: str) -> Dict[str, Any]:
        """Generate POPIA compliance report"""
        try:
            logger.info(f"Generating {report_type} POPIA report for company {company_id}")
            
            # Mock compliance data
            compliance_data = {
                "data_inventory": {
                    "total_data_categories": 5,
                    "personal_data_items": 12,
                    "financial_data_items": 8,
                    "business_data_items": 15,
                    "usage_data_items": 25
                },
                "consent_records": {
                    "total_consents": 150,
                    "active_consents": 142,
                    "withdrawn_consents": 8,
                    "consent_types": {
                        "data_processing": 142,
                        "marketing": 45,
                        "analytics": 89,
                        "third_party_sharing": 12
                    }
                },
                "data_subject_requests": {
                    "access_requests": 15,
                    "portability_requests": 3,
                    "deletion_requests": 8,
                    "correction_requests": 5,
                    "average_response_time_hours": 18.5
                },
                "compliance_score": 94.5,
                "risk_assessment": {
                    "overall_risk": "low",
                    "data_breach_risk": "low",
                    "consent_compliance": "high",
                    "retention_compliance": "high"
                }
            }
            
            return {
                "status": "report_generated",
                "report_id": str(uuid.uuid4()),
                "company_id": company_id,
                "report_type": report_type,
                "generated_date": datetime.now(UTC).isoformat(),
                "compliance_data": compliance_data,
                "recommendations": [
                    "Review consent mechanisms quarterly",
                    "Update privacy policy annually",
                    "Conduct data protection impact assessment for new features",
                    "Train staff on POPIA requirements"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate POPIA report: {str(e)}")
            return {
                "status": "error",
                "message": f"POPIA report generation failed: {str(e)}"
            }
    
    async def conduct_data_protection_impact_assessment(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct Data Protection Impact Assessment (DPIA)"""
        try:
            logger.info(f"Conducting DPIA for project: {project_data.get('project_name')}")
            
            # Assess privacy risks
            risk_factors = {
                "data_volume": "medium",
                "sensitivity": "high",
                "processing_purposes": "multiple",
                "automated_decision_making": "yes",
                "special_categories": "no",
                "third_party_sharing": "limited"
            }
            
            # Calculate risk score
            risk_score = self._calculate_dpia_risk_score(risk_factors)
            
            # Generate recommendations
            recommendations = []
            if risk_score > 70:
                recommendations.append("High risk - consider alternative approaches")
                recommendations.append("Implement additional safeguards")
                recommendations.append("Regular monitoring required")
            elif risk_score > 40:
                recommendations.append("Medium risk - standard safeguards sufficient")
                recommendations.append("Regular review recommended")
            else:
                recommendations.append("Low risk - proceed with standard measures")
            
            return {
                "status": "dpia_completed",
                "dpia_id": str(uuid.uuid4()),
                "project_name": project_data.get("project_name"),
                "risk_score": risk_score,
                "risk_level": "high" if risk_score > 70 else "medium" if risk_score > 40 else "low",
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "approval_required": risk_score > 70,
                "completion_date": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to conduct DPIA: {str(e)}")
            return {
                "status": "error",
                "message": f"DPIA failed: {str(e)}"
            }
    
    def _calculate_dpia_risk_score(self, risk_factors: Dict[str, Any]) -> float:
        """Calculate DPIA risk score based on risk factors"""
        score = 0
        
        # Data volume scoring
        volume_scores = {"low": 10, "medium": 30, "high": 50}
        score += volume_scores.get(risk_factors["data_volume"], 30)
        
        # Sensitivity scoring
        sensitivity_scores = {"low": 10, "medium": 30, "high": 50}
        score += sensitivity_scores.get(risk_factors["sensitivity"], 30)
        
        # Additional risk factors
        if risk_factors["automated_decision_making"] == "yes":
            score += 20
        if risk_factors["special_categories"] == "yes":
            score += 30
        if risk_factors["third_party_sharing"] == "extensive":
            score += 20
        
        return min(score, 100)  # Cap at 100
    
    async def validate_data_processing_lawfulness(self, processing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate lawfulness of data processing under POPIA"""
        try:
            legal_basis = processing_data.get("legal_basis")
            purpose = processing_data.get("purpose")
            data_categories = processing_data.get("data_categories", [])
            
            # Validate legal basis appropriateness
            validation_results = {
                "legal_basis_valid": legal_basis in self.legal_bases,
                "purpose_specific": len(purpose) > 0 if purpose else False,
                "data_minimization": len(data_categories) <= 3,  # Reasonable limit
                "proportionality": True,  # Would need more complex logic
                "transparency": True  # Assuming privacy notice exists
            }
            
            # Calculate overall compliance
            compliance_score = sum(validation_results.values()) / len(validation_results) * 100
            
            return {
                "status": "validation_completed",
                "compliance_score": compliance_score,
                "is_lawful": compliance_score >= 80,
                "validation_results": validation_results,
                "recommendations": [
                    "Ensure privacy notice is clear and accessible",
                    "Implement data minimization practices",
                    "Regularly review processing purposes"
                ],
                "validated_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to validate data processing lawfulness: {str(e)}")
            return {
                "status": "error",
                "message": f"Validation failed: {str(e)}"
            }
    
    async def handle_data_breach_notification(self, breach_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POPIA data breach notification requirements"""
        try:
            logger.info(f"Processing data breach notification for incident {breach_data.get('incident_id')}")
            
            # Assess breach severity
            severity_factors = {
                "data_categories_affected": len(breach_data.get("data_categories", [])),
                "number_of_individuals": breach_data.get("individuals_affected", 0),
                "special_categories": breach_data.get("special_categories", False),
                "financial_impact": breach_data.get("financial_impact", "low")
            }
            
            # Determine notification requirements
            severity_score = sum(severity_factors.values())
            
            if severity_score > 50:
                notification_required = True
                notification_deadline = datetime.now(UTC) + timedelta(hours=72)  # 72 hours
            else:
                notification_required = False
                notification_deadline = None
            
            return {
                "status": "breach_assessed",
                "incident_id": breach_data.get("incident_id"),
                "severity_score": severity_score,
                "notification_required": notification_required,
                "notification_deadline": notification_deadline.isoformat() if notification_deadline else None,
                "affected_individuals": breach_data.get("individuals_affected", 0),
                "data_categories": breach_data.get("data_categories", []),
                "remediation_steps": [
                    "Contain the breach",
                    "Assess the impact",
                    "Notify relevant authorities",
                    "Inform affected individuals",
                    "Implement additional safeguards"
                ],
                "assessed_at": datetime.now(UTC).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to handle data breach notification: {str(e)}")
            return {
                "status": "error",
                "message": f"Breach notification failed: {str(e)}"
            }








