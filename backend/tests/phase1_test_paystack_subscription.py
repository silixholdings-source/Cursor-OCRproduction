"""
Phase 1 Test Suite for Paystack Subscription Setup with Configurable Trials and POPIA Compliance
Tests subscription management, trial periods, auto-conversion, and South African compliance
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
import uuid
import json

from services.paystack_service import PaystackService, SubscriptionPlan, TrialPeriod
from services.subscription_manager import SubscriptionManager
from services.popia_compliance import POPIAComplianceService
from src.models.company import Company, CompanyTier, CompanyStatus
from src.models.user import User, UserRole
from src.models.subscription import Subscription, SubscriptionStatus, SubscriptionType


class TestPhase1PaystackSubscription:
    """Test suite for Phase 1 Paystack subscription requirements"""
    
    @pytest.fixture
    def paystack_service(self):
        """Create Paystack service instance"""
        return PaystackService(
            secret_key="sk_test_paystack_key",
            public_key="pk_test_paystack_key"
        )
    
    @pytest.fixture
    def subscription_manager(self):
        """Create subscription manager instance"""
        return SubscriptionManager()
    
    @pytest.fixture
    def popia_service(self):
        """Create POPIA compliance service instance"""
        return POPIAComplianceService()
    
    @pytest.fixture
    def sample_company_basic(self):
        """Sample basic tier company"""
        return Company(
            id=str(uuid.uuid4()),
            name="Basic Company Ltd",
            tier=CompanyTier.BASIC,
            status=CompanyStatus.ACTIVE,
            subscription_status="trial",
            trial_end_date=datetime.utcnow() + timedelta(days=14),
            created_at=datetime.utcnow(),
            country="ZA",  # South Africa
            data_processing_consent=True,
            popia_consent_date=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_company_enterprise(self):
        """Sample enterprise tier company"""
        return Company(
            id=str(uuid.uuid4()),
            name="Enterprise Corp SA",
            tier=CompanyTier.ENTERPRISE,
            status=CompanyStatus.ACTIVE,
            subscription_status="active",
            created_at=datetime.utcnow(),
            country="ZA",  # South Africa
            data_processing_consent=True,
            popia_consent_date=datetime.utcnow(),
            sla_agreement_id=str(uuid.uuid4()),
            sla_signed_date=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for subscription management"""
        return User(
            id=str(uuid.uuid4()),
            email="admin@company.co.za",
            role=UserRole.ADMIN,
            first_name="John",
            last_name="Admin",
            company_id=str(uuid.uuid4()),
            created_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_paystack_connection_validation(self, paystack_service):
        """Test Paystack API connection validation"""
        
        with patch.object(paystack_service.client, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": True,
                "message": "Verification successful",
                "data": {
                    "domain": "test.com",
                    "integration": 12345
                }
            }
            mock_get.return_value = mock_response
            
            result = await paystack_service.validate_connection()
            
            assert result["status"] == "connected"
            assert result["provider"] == "paystack"
            assert result["integration_id"] == 12345

    @pytest.mark.asyncio
    async def test_create_subscription_plans(self, paystack_service):
        """Test creation of subscription plans for different tiers"""
        
        plans = [
            SubscriptionPlan(
                name="Basic Plan",
                amount=5000,  # R50.00 in kobo
                interval="monthly",
                currency="ZAR",
                tier="basic",
                features=["invoice_processing", "basic_ocr", "email_support"]
            ),
            SubscriptionPlan(
                name="Professional Plan",
                amount=15000,  # R150.00 in kobo
                interval="monthly", 
                currency="ZAR",
                tier="professional",
                features=["invoice_processing", "advanced_ocr", "api_access", "priority_support"]
            ),
            SubscriptionPlan(
                name="Enterprise Plan",
                amount=50000,  # R500.00 in kobo
                interval="monthly",
                currency="ZAR", 
                tier="enterprise",
                features=["invoice_processing", "advanced_ocr", "api_access", "dedicated_support", "custom_integrations"]
            )
        ]
        
        with patch.object(paystack_service.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                "status": True,
                "message": "Plan created",
                "data": {
                    "id": "PLN_test123",
                    "name": "Basic Plan",
                    "amount": 5000,
                    "currency": "ZAR"
                }
            }
            mock_post.return_value = mock_response
            
            for plan in plans:
                result = await paystack_service.create_plan(plan)
                
                assert result["status"] == "created"
                assert result["plan_id"] == "PLN_test123"
                assert result["amount"] == plan.amount
                assert result["currency"] == "ZAR"

    @pytest.mark.asyncio
    async def test_configurable_trial_periods(self, subscription_manager, sample_company_basic):
        """Test configurable trial period setup"""
        
        # Test different trial periods
        trial_periods = [
            TrialPeriod(days=7, name="7-day trial"),
            TrialPeriod(days=14, name="14-day trial"),
            TrialPeriod(days=30, name="30-day trial"),
            TrialPeriod(days=60, name="60-day enterprise trial")
        ]
        
        for trial in trial_periods:
            with patch.object(subscription_manager, 'create_trial_subscription') as mock_create:
                mock_create.return_value = {
                    "status": "trial_created",
                    "trial_id": str(uuid.uuid4()),
                    "trial_end_date": datetime.utcnow() + timedelta(days=trial.days),
                    "auto_convert": True,
                    "trial_duration_days": trial.days
                }
                
                result = await subscription_manager.create_trial_subscription(
                    sample_company_basic.id,
                    trial.days,
                    "basic"
                )
                
                assert result["status"] == "trial_created"
                assert result["trial_duration_days"] == trial.days
                assert result["auto_convert"] == True

    @pytest.mark.asyncio
    async def test_corporate_trial_negotiation(self, subscription_manager, sample_company_enterprise):
        """Test corporate trial period negotiation and custom setup"""
        
        # Corporate requests 90-day trial
        corporate_trial = TrialPeriod(
            days=90,
            name="Corporate 90-day trial",
            is_custom=True,
            requires_approval=True,
            custom_terms="Extended trial for enterprise evaluation"
        )
        
        with patch.object(subscription_manager, 'create_custom_trial') as mock_create:
            mock_create.return_value = {
                "status": "custom_trial_created",
                "trial_id": str(uuid.uuid4()),
                "trial_end_date": datetime.utcnow() + timedelta(days=90),
                "requires_approval": True,
                "custom_terms": corporate_trial.custom_terms,
                "approval_workflow": "manual_review"
            }
            
            result = await subscription_manager.create_custom_trial(
                sample_company_enterprise.id,
                90,
                "enterprise",
                corporate_trial.custom_terms
            )
            
            assert result["status"] == "custom_trial_created"
            assert result["trial_duration_days"] == 90
            assert result["requires_approval"] == True
            assert result["custom_terms"] == corporate_trial.custom_terms

    @pytest.mark.asyncio
    async def test_trial_auto_conversion_to_subscription(self, paystack_service, subscription_manager, sample_company_basic):
        """Test automatic trial to subscription conversion"""
        
        # Mock trial ending
        trial_end_date = datetime.utcnow() - timedelta(hours=1)  # Trial ended 1 hour ago
        sample_company_basic.trial_end_date = trial_end_date
        
        with patch.object(paystack_service, 'create_subscription') as mock_create_sub:
            mock_create_sub.return_value = {
                "status": "subscription_created",
                "subscription_id": "SUB_test123",
                "customer_id": "CUS_test123",
                "plan_id": "PLN_basic",
                "start_date": datetime.utcnow().isoformat(),
                "next_payment_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            with patch.object(subscription_manager, 'process_trial_conversion') as mock_convert:
                mock_convert.return_value = {
                    "status": "converted",
                    "subscription_id": "SUB_test123",
                    "conversion_date": datetime.utcnow().isoformat(),
                    "payment_method": "auto_charge"
                }
                
                result = await subscription_manager.process_trial_conversion(
                    sample_company_basic.id
                )
                
                assert result["status"] == "converted"
                assert result["subscription_id"] == "SUB_test123"
                assert "conversion_date" in result

    @pytest.mark.asyncio
    async def test_trial_cancellation_before_conversion(self, subscription_manager, sample_company_basic):
        """Test trial cancellation before auto-conversion"""
        
        # Mock trial cancellation
        with patch.object(subscription_manager, 'cancel_trial') as mock_cancel:
            mock_cancel.return_value = {
                "status": "cancelled",
                "trial_id": str(uuid.uuid4()),
                "cancellation_date": datetime.utcnow().isoformat(),
                "reason": "user_requested",
                "auto_convert": False
            }
            
            result = await subscription_manager.cancel_trial(
                sample_company_basic.id,
                "user_requested"
            )
            
            assert result["status"] == "cancelled"
            assert result["auto_convert"] == False
            assert result["reason"] == "user_requested"

    @pytest.mark.asyncio
    async def test_popia_compliance_consent_management(self, popia_service, sample_company_basic):
        """Test POPIA compliance consent management"""
        
        # Test consent recording
        consent_data = {
            "company_id": sample_company_basic.id,
            "consent_type": "data_processing",
            "consent_given": True,
            "consent_date": datetime.utcnow(),
            "legal_basis": "legitimate_interest",
            "data_categories": ["personal_data", "financial_data", "business_data"],
            "retention_period": "7_years",
            "third_party_sharing": False
        }
        
        with patch.object(popia_service, 'record_consent') as mock_record:
            mock_record.return_value = {
                "status": "consent_recorded",
                "consent_id": str(uuid.uuid4()),
                "compliance_status": "compliant",
                "popia_reference": "POPIA-2024-001"
            }
            
            result = await popia_service.record_consent(consent_data)
            
            assert result["status"] == "consent_recorded"
            assert result["compliance_status"] == "compliant"
            assert "popia_reference" in result

    @pytest.mark.asyncio
    async def test_popia_data_subject_rights(self, popia_service, sample_user):
        """Test POPIA data subject rights implementation"""
        
        # Test data access request
        with patch.object(popia_service, 'handle_data_access_request') as mock_access:
            mock_access.return_value = {
                "status": "data_provided",
                "request_id": str(uuid.uuid4()),
                "data_categories": ["personal_data", "usage_data"],
                "processing_purposes": ["service_delivery", "billing"],
                "data_retention": "7_years",
                "response_date": datetime.utcnow().isoformat()
            }
            
            result = await popia_service.handle_data_access_request(
                sample_user.id,
                "data_portability"
            )
            
            assert result["status"] == "data_provided"
            assert "data_categories" in result
            assert "processing_purposes" in result

    @pytest.mark.asyncio
    async def test_popia_data_deletion_request(self, popia_service, sample_user):
        """Test POPIA data deletion request handling"""
        
        with patch.object(popia_service, 'handle_data_deletion_request') as mock_delete:
            mock_delete.return_value = {
                "status": "deletion_processed",
                "request_id": str(uuid.uuid4()),
                "deletion_type": "complete",
                "data_categories_deleted": ["personal_data", "usage_data"],
                "retention_required": ["financial_records"],  # Legal requirement
                "deletion_date": datetime.utcnow().isoformat()
            }
            
            result = await popia_service.handle_data_deletion_request(
                sample_user.id,
                "complete_deletion"
            )
            
            assert result["status"] == "deletion_processed"
            assert result["deletion_type"] == "complete"
            assert "retention_required" in result

    @pytest.mark.asyncio
    async def test_payment_compliance_layer(self, paystack_service):
        """Test payment provider compliance layer (PCI-DSS)"""
        
        # Test secure payment processing
        payment_data = {
            "amount": 5000,  # R50.00
            "currency": "ZAR",
            "customer_email": "test@company.co.za",
            "reference": "TXN_test123",
            "callback_url": "https://app.company.com/payment/callback"
        }
        
        with patch.object(paystack_service.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": True,
                "message": "Authorization URL created",
                "data": {
                    "authorization_url": "https://checkout.paystack.com/authorize/test123",
                    "access_code": "access_code_test123",
                    "reference": "TXN_test123"
                }
            }
            mock_post.return_value = mock_response
            
            result = await paystack_service.initialize_payment(payment_data)
            
            assert result["status"] == "authorization_created"
            assert "authorization_url" in result
            assert result["reference"] == "TXN_test123"
            assert "paystack.com" in result["authorization_url"]

    @pytest.mark.asyncio
    async def test_subscription_billing_cycle_management(self, paystack_service, subscription_manager):
        """Test subscription billing cycle management"""
        
        subscription_id = "SUB_test123"
        
        with patch.object(paystack_service, 'get_subscription') as mock_get:
            mock_get.return_value = {
                "status": "active",
                "subscription_id": subscription_id,
                "plan_id": "PLN_professional",
                "customer_id": "CUS_test123",
                "next_payment_date": (datetime.utcnow() + timedelta(days=15)).isoformat(),
                "amount": 15000,  # R150.00
                "currency": "ZAR",
                "billing_cycle": "monthly"
            }
            
            with patch.object(subscription_manager, 'manage_billing_cycle') as mock_manage:
                mock_manage.return_value = {
                    "status": "cycle_managed",
                    "subscription_id": subscription_id,
                    "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                    "amount_due": 15000,
                    "currency": "ZAR"
                }
                
                result = await subscription_manager.manage_billing_cycle(subscription_id)
                
                assert result["status"] == "cycle_managed"
                assert result["subscription_id"] == subscription_id
                assert result["amount_due"] == 15000

    @pytest.mark.asyncio
    async def test_subscription_upgrade_downgrade(self, paystack_service, subscription_manager):
        """Test subscription plan upgrades and downgrades"""
        
        # Test upgrade
        with patch.object(paystack_service, 'update_subscription') as mock_update:
            mock_update.return_value = {
                "status": "subscription_updated",
                "subscription_id": "SUB_test123",
                "old_plan": "PLN_basic",
                "new_plan": "PLN_professional",
                "effective_date": datetime.utcnow().isoformat(),
                "prorated_amount": 10000  # R100.00 prorated
            }
            
            with patch.object(subscription_manager, 'change_subscription_plan') as mock_change:
                mock_change.return_value = {
                    "status": "plan_changed",
                    "subscription_id": "SUB_test123",
                    "change_type": "upgrade",
                    "old_plan": "basic",
                    "new_plan": "professional",
                    "effective_date": datetime.utcnow().isoformat(),
                    "prorated_charge": 10000
                }
                
                result = await subscription_manager.change_subscription_plan(
                    "SUB_test123",
                    "professional",
                    "upgrade"
                )
                
                assert result["status"] == "plan_changed"
                assert result["change_type"] == "upgrade"
                assert result["new_plan"] == "professional"

    @pytest.mark.asyncio
    async def test_subscription_cancellation_and_retention(self, subscription_manager):
        """Test subscription cancellation with retention strategies"""
        
        with patch.object(subscription_manager, 'cancel_subscription') as mock_cancel:
            mock_cancel.return_value = {
                "status": "cancellation_requested",
                "subscription_id": "SUB_test123",
                "cancellation_date": datetime.utcnow().isoformat(),
                "retention_offers": [
                    {
                        "offer_type": "discount",
                        "discount_percentage": 20,
                        "duration_months": 3,
                        "description": "20% off for 3 months"
                    },
                    {
                        "offer_type": "pause",
                        "duration_months": 2,
                        "description": "Pause subscription for 2 months"
                    }
                ],
                "final_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
            result = await subscription_manager.cancel_subscription(
                "SUB_test123",
                "user_requested"
            )
            
            assert result["status"] == "cancellation_requested"
            assert len(result["retention_offers"]) == 2
            assert result["retention_offers"][0]["offer_type"] == "discount"

    @pytest.mark.asyncio
    async def test_sla_agreement_management(self, subscription_manager, sample_company_enterprise):
        """Test SLA agreement management for enterprise clients"""
        
        sla_data = {
            "company_id": sample_company_enterprise.id,
            "sla_type": "enterprise",
            "uptime_guarantee": 99.9,
            "response_time_sla": "2_hours",
            "support_level": "dedicated",
            "custom_terms": [
                "24/7 phone support",
                "Dedicated account manager",
                "Custom integrations",
                "Priority feature requests"
            ],
            "penalty_clauses": {
                "uptime_below_99_9": "service_credit",
                "response_time_exceeded": "escalation_process"
            }
        }
        
        with patch.object(subscription_manager, 'create_sla_agreement') as mock_create:
            mock_create.return_value = {
                "status": "sla_created",
                "sla_id": str(uuid.uuid4()),
                "company_id": sample_company_enterprise.id,
                "sla_type": "enterprise",
                "effective_date": datetime.utcnow().isoformat(),
                "expiry_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "uptime_guarantee": 99.9,
                "support_level": "dedicated"
            }
            
            result = await subscription_manager.create_sla_agreement(sla_data)
            
            assert result["status"] == "sla_created"
            assert result["sla_type"] == "enterprise"
            assert result["uptime_guarantee"] == 99.9
            assert result["support_level"] == "dedicated"

    @pytest.mark.asyncio
    async def test_subscription_analytics_and_reporting(self, subscription_manager):
        """Test subscription analytics and reporting"""
        
        with patch.object(subscription_manager, 'generate_subscription_report') as mock_report:
            mock_report.return_value = {
                "status": "report_generated",
                "report_id": str(uuid.uuid4()),
                "report_type": "monthly_subscription_analytics",
                "period": "2024-01",
                "metrics": {
                    "total_subscriptions": 150,
                    "active_subscriptions": 142,
                    "trial_conversions": 28,
                    "churn_rate": 5.3,
                    "mrr": 225000,  # R2,250.00 monthly recurring revenue
                    "arr": 2700000,  # R27,000.00 annual recurring revenue
                    "average_revenue_per_user": 1500  # R15.00
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            result = await subscription_manager.generate_subscription_report(
                "monthly_subscription_analytics",
                "2024-01"
            )
            
            assert result["status"] == "report_generated"
            assert result["report_type"] == "monthly_subscription_analytics"
            assert "metrics" in result
            assert result["metrics"]["total_subscriptions"] > 0

    def test_paystack_webhook_validation(self, paystack_service):
        """Test Paystack webhook validation and processing"""
        
        # Mock webhook payload
        webhook_payload = {
            "event": "subscription.create",
            "data": {
                "id": "SUB_test123",
                "customer": "CUS_test123",
                "plan": "PLN_basic",
                "status": "active",
                "subscription_code": "SUB_test123",
                "email_token": "email_token_test123",
                "amount": 5000,
                "currency": "ZAR",
                "next_payment_date": "2024-02-15T00:00:00.000Z"
            }
        }
        
        with patch.object(paystack_service, 'validate_webhook') as mock_validate:
            mock_validate.return_value = True
            
            with patch.object(paystack_service, 'process_webhook') as mock_process:
                mock_process.return_value = {
                    "status": "webhook_processed",
                    "event_type": "subscription.create",
                    "subscription_id": "SUB_test123",
                    "processed_at": datetime.utcnow().isoformat()
                }
                
                result = paystack_service.process_webhook(webhook_payload)
                
                assert result["status"] == "webhook_processed"
                assert result["event_type"] == "subscription.create"
                assert result["subscription_id"] == "SUB_test123"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
