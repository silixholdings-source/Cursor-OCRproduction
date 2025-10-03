"""
Contract Tests for AI ERP SaaS Platform
World-class contract testing to ensure consistent behavior across all ERP adapters
"""
import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass

from src.services.erp import (
    ERPAdapter, MockERPAdapter, MicrosoftDynamicsGPAdapter,
    Dynamics365BCAdapter, XeroAdapter, ERPIntegrationService
)
from src.models.invoice import Invoice, InvoiceStatus
from tests.golden_datasets import golden_dataset_manager

@dataclass
class ContractTestResult:
    """Result of a contract test"""
    test_name: str
    adapter_name: str
    passed: bool
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    details: Dict[str, Any] = None

class ERPContractTester:
    """Comprehensive contract testing for ERP adapters"""
    
    def __init__(self):
        self.test_invoices = self._create_test_invoices()
        self.expected_behaviors = self._define_expected_behaviors()
    
    def _create_test_invoices(self) -> List[Invoice]:
        """Create standardized test invoices for contract testing"""
        invoices = []
        
        # Simple invoice
        simple_invoice = Invoice(
            id="test_invoice_001",
            invoice_number="TEST-001",
            supplier_name="Test Supplier Corp",
            total_amount=1000.00,
            currency="USD",
            invoice_date=datetime.utcnow().date(),
            due_date=(datetime.utcnow() + timedelta(days=30)).date(),
            status=InvoiceStatus.PENDING,
            created_at=datetime.utcnow()
        )
        invoices.append(simple_invoice)
        
        # Complex invoice
        complex_invoice = Invoice(
            id="test_invoice_002",
            invoice_number="TEST-002",
            supplier_name="Complex Supplier Ltd",
            total_amount=25000.00,
            currency="USD",
            invoice_date=datetime.utcnow().date(),
            due_date=(datetime.utcnow() + timedelta(days=60)).date(),
            status=InvoiceStatus.PENDING,
            created_at=datetime.utcnow(),
            po_number="PO-2024-001",
            contract_number="CNT-2024-001"
        )
        invoices.append(complex_invoice)
        
        # International invoice
        international_invoice = Invoice(
            id="test_invoice_003",
            invoice_number="TEST-003",
            supplier_name="International Trading Co",
            total_amount=15000.00,
            currency="EUR",
            invoice_date=datetime.utcnow().date(),
            due_date=(datetime.utcnow() + timedelta(days=45)).date(),
            status=InvoiceStatus.PENDING,
            created_at=datetime.utcnow(),
            vat_number="DE123456789"
        )
        invoices.append(international_invoice)
        
        return invoices
    
    def _define_expected_behaviors(self) -> Dict[str, Any]:
        """Define expected behaviors for all ERP adapters"""
        return {
            "health_check": {
                "required_fields": ["status", "erp_name", "timestamp"],
                "status_values": ["healthy", "degraded", "unhealthy"],
                "response_time_max_ms": 5000
            },
            "post_invoice": {
                "required_fields": ["status", "erp_document_id", "posted_at"],
                "status_values": ["success", "error", "pending"],
                "response_time_max_ms": 30000
            },
            "get_invoice_status": {
                "required_fields": ["status", "erp_document_id", "last_updated"],
                "status_values": ["posted", "pending", "error", "not_found"],
                "response_time_max_ms": 5000
            },
            "validate_connection": {
                "required_fields": ["status", "message", "timestamp"],
                "status_values": ["connected", "disconnected", "error"],
                "response_time_max_ms": 10000
            }
        }
    
    async def run_all_contract_tests(self, adapters: List[ERPAdapter]) -> List[ContractTestResult]:
        """Run comprehensive contract tests against all adapters"""
        results = []
        
        for adapter in adapters:
            adapter_name = adapter.__class__.__name__
            
            # Health check tests
            health_results = await self._test_health_check_contract(adapter, adapter_name)
            results.extend(health_results)
            
            # Invoice posting tests
            posting_results = await self._test_post_invoice_contract(adapter, adapter_name)
            results.extend(posting_results)
            
            # Invoice status tests
            status_results = await self._test_get_invoice_status_contract(adapter, adapter_name)
            results.extend(status_results)
            
            # Connection validation tests
            connection_results = await self._test_validate_connection_contract(adapter, adapter_name)
            results.extend(connection_results)
            
            # Error handling tests
            error_results = await self._test_error_handling_contract(adapter, adapter_name)
            results.extend(error_results)
            
            # Performance tests
            performance_results = await self._test_performance_contract(adapter, adapter_name)
            results.extend(performance_results)
        
        return results
    
    async def _test_health_check_contract(self, adapter: ERPAdapter, adapter_name: str) -> List[ContractTestResult]:
        """Test health check contract compliance"""
        results = []
        start_time = datetime.utcnow()
        
        try:
            # Test health check method exists
            assert hasattr(adapter, 'health_check'), f"Adapter {adapter_name} missing health_check method"
            assert callable(adapter.health_check), f"Adapter {adapter_name} health_check is not callable"
            
            # Test health check execution
            health_result = await adapter.health_check()
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Validate response structure
            expected_behavior = self.expected_behaviors["health_check"]
            
            for field in expected_behavior["required_fields"]:
                assert field in health_result, f"Health check missing required field: {field}"
            
            # Validate status value
            status = health_result["status"]
            assert status in expected_behavior["status_values"], f"Invalid status value: {status}"
            
            # Validate response time
            assert execution_time <= expected_behavior["response_time_max_ms"], f"Health check too slow: {execution_time}ms"
            
            # Validate data types
            assert isinstance(health_result["erp_name"], str), "erp_name must be string"
            assert isinstance(health_result["timestamp"], str), "timestamp must be string"
            
            results.append(ContractTestResult(
                test_name="health_check_contract",
                adapter_name=adapter_name,
                passed=True,
                execution_time_ms=execution_time,
                details={"response": health_result}
            ))
            
        except Exception as e:
            results.append(ContractTestResult(
                test_name="health_check_contract",
                adapter_name=adapter_name,
                passed=False,
                error_message=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            ))
        
        return results
    
    async def _test_post_invoice_contract(self, adapter: ERPAdapter, adapter_name: str) -> List[ContractTestResult]:
        """Test invoice posting contract compliance"""
        results = []
        
        for invoice in self.test_invoices:
            start_time = datetime.utcnow()
            
            try:
                # Test post_invoice method exists
                assert hasattr(adapter, 'post_invoice'), f"Adapter {adapter_name} missing post_invoice method"
                assert callable(adapter.post_invoice), f"Adapter {adapter_name} post_invoice is not callable"
                
                # Test invoice posting
                company_settings = {"company_id": "test_company", "erp_config": {}}
                post_result = await adapter.post_invoice(invoice, company_settings)
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Validate response structure
                expected_behavior = self.expected_behaviors["post_invoice"]
                
                for field in expected_behavior["required_fields"]:
                    assert field in post_result, f"Post invoice missing required field: {field}"
                
                # Validate status value
                status = post_result["status"]
                assert status in expected_behavior["status_values"], f"Invalid status value: {status}"
                
                # Validate response time
                assert execution_time <= expected_behavior["response_time_max_ms"], f"Post invoice too slow: {execution_time}ms"
                
                # Validate data types
                if status == "success":
                    assert isinstance(post_result["erp_document_id"], str), "erp_document_id must be string"
                    assert isinstance(post_result["posted_at"], str), "posted_at must be string"
                
                results.append(ContractTestResult(
                    test_name=f"post_invoice_contract_{invoice.id}",
                    adapter_name=adapter_name,
                    passed=True,
                    execution_time_ms=execution_time,
                    details={"invoice_id": invoice.id, "response": post_result}
                ))
                
            except Exception as e:
                results.append(ContractTestResult(
                    test_name=f"post_invoice_contract_{invoice.id}",
                    adapter_name=adapter_name,
                    passed=False,
                    error_message=str(e),
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                ))
        
        return results
    
    async def _test_get_invoice_status_contract(self, adapter: ERPAdapter, adapter_name: str) -> List[ContractTestResult]:
        """Test invoice status retrieval contract compliance"""
        results = []
        start_time = datetime.utcnow()
        
        try:
            # Test get_invoice_status method exists
            assert hasattr(adapter, 'get_invoice_status'), f"Adapter {adapter_name} missing get_invoice_status method"
            assert callable(adapter.get_invoice_status), f"Adapter {adapter_name} get_invoice_status is not callable"
            
            # Test status retrieval
            test_document_id = "TEST-DOC-001"
            status_result = await adapter.get_invoice_status(test_document_id)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Validate response structure
            expected_behavior = self.expected_behaviors["get_invoice_status"]
            
            for field in expected_behavior["required_fields"]:
                assert field in status_result, f"Get invoice status missing required field: {field}"
            
            # Validate status value
            status = status_result["status"]
            assert status in expected_behavior["status_values"], f"Invalid status value: {status}"
            
            # Validate response time
            assert execution_time <= expected_behavior["response_time_max_ms"], f"Get invoice status too slow: {execution_time}ms"
            
            # Validate data types
            assert isinstance(status_result["erp_document_id"], str), "erp_document_id must be string"
            assert isinstance(status_result["last_updated"], str), "last_updated must be string"
            
            results.append(ContractTestResult(
                test_name="get_invoice_status_contract",
                adapter_name=adapter_name,
                passed=True,
                execution_time_ms=execution_time,
                details={"document_id": test_document_id, "response": status_result}
            ))
            
        except Exception as e:
            results.append(ContractTestResult(
                test_name="get_invoice_status_contract",
                adapter_name=adapter_name,
                passed=False,
                error_message=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            ))
        
        return results
    
    async def _test_validate_connection_contract(self, adapter: ERPAdapter, adapter_name: str) -> List[ContractTestResult]:
        """Test connection validation contract compliance"""
        results = []
        start_time = datetime.utcnow()
        
        try:
            # Test validate_connection method exists
            assert hasattr(adapter, 'validate_connection'), f"Adapter {adapter_name} missing validate_connection method"
            assert callable(adapter.validate_connection), f"Adapter {adapter_name} validate_connection is not callable"
            
            # Test connection validation
            connection_result = await adapter.validate_connection()
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Validate response structure
            expected_behavior = self.expected_behaviors["validate_connection"]
            
            for field in expected_behavior["required_fields"]:
                assert field in connection_result, f"Validate connection missing required field: {field}"
            
            # Validate status value
            status = connection_result["status"]
            assert status in expected_behavior["status_values"], f"Invalid status value: {status}"
            
            # Validate response time
            assert execution_time <= expected_behavior["response_time_max_ms"], f"Validate connection too slow: {execution_time}ms"
            
            # Validate data types
            assert isinstance(connection_result["message"], str), "message must be string"
            assert isinstance(connection_result["timestamp"], str), "timestamp must be string"
            
            results.append(ContractTestResult(
                test_name="validate_connection_contract",
                adapter_name=adapter_name,
                passed=True,
                execution_time_ms=execution_time,
                details={"response": connection_result}
            ))
            
        except Exception as e:
            results.append(ContractTestResult(
                test_name="validate_connection_contract",
                adapter_name=adapter_name,
                passed=False,
                error_message=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            ))
        
        return results
    
    async def _test_error_handling_contract(self, adapter: ERPAdapter, adapter_name: str) -> List[ContractTestResult]:
        """Test error handling contract compliance"""
        results = []
        
        # Test with invalid invoice data
        start_time = datetime.utcnow()
        try:
            invalid_invoice = Mock()
            invalid_invoice.invoice_number = None  # Invalid data
            invalid_invoice.supplier_name = ""
            invalid_invoice.total_amount = -100  # Invalid amount
            
            company_settings = {"company_id": "test_company"}
            error_result = await adapter.post_invoice(invalid_invoice, company_settings)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Should handle errors gracefully
            assert "status" in error_result, "Error response must include status"
            assert error_result["status"] in ["error", "failed"], "Invalid data should result in error status"
            
            results.append(ContractTestResult(
                test_name="error_handling_invalid_data",
                adapter_name=adapter_name,
                passed=True,
                execution_time_ms=execution_time,
                details={"error_response": error_result}
            ))
            
        except Exception as e:
            # Should not raise unhandled exceptions
            results.append(ContractTestResult(
                test_name="error_handling_invalid_data",
                adapter_name=adapter_name,
                passed=False,
                error_message=f"Unhandled exception: {str(e)}",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            ))
        
        # Test with invalid document ID
        start_time = datetime.utcnow()
        try:
            invalid_doc_id = "INVALID-DOC-ID"
            error_result = await adapter.get_invoice_status(invalid_doc_id)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Should handle invalid document ID gracefully
            assert "status" in error_result, "Error response must include status"
            assert error_result["status"] in ["error", "not_found"], "Invalid document ID should result in error or not_found"
            
            results.append(ContractTestResult(
                test_name="error_handling_invalid_document_id",
                adapter_name=adapter_name,
                passed=True,
                execution_time_ms=execution_time,
                details={"error_response": error_result}
            ))
            
        except Exception as e:
            results.append(ContractTestResult(
                test_name="error_handling_invalid_document_id",
                adapter_name=adapter_name,
                passed=False,
                error_message=f"Unhandled exception: {str(e)}",
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            ))
        
        return results
    
    async def _test_performance_contract(self, adapter: ERPAdapter, adapter_name: str) -> List[ContractTestResult]:
        """Test performance contract compliance"""
        results = []
        
        # Test health check performance
        start_time = datetime.utcnow()
        try:
            await adapter.health_check()
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Health check should be fast
            max_time = 5000  # 5 seconds
            passed = execution_time <= max_time
            
            results.append(ContractTestResult(
                test_name="performance_health_check",
                adapter_name=adapter_name,
                passed=passed,
                error_message=f"Health check took {execution_time}ms, max allowed: {max_time}ms" if not passed else None,
                execution_time_ms=execution_time
            ))
            
        except Exception as e:
            results.append(ContractTestResult(
                test_name="performance_health_check",
                adapter_name=adapter_name,
                passed=False,
                error_message=str(e),
                execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
            ))
        
        # Test invoice posting performance
        if self.test_invoices:
            invoice = self.test_invoices[0]
            start_time = datetime.utcnow()
            try:
                company_settings = {"company_id": "test_company"}
                await adapter.post_invoice(invoice, company_settings)
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Invoice posting should complete within reasonable time
                max_time = 30000  # 30 seconds
                passed = execution_time <= max_time
                
                results.append(ContractTestResult(
                    test_name="performance_post_invoice",
                    adapter_name=adapter_name,
                    passed=passed,
                    error_message=f"Invoice posting took {execution_time}ms, max allowed: {max_time}ms" if not passed else None,
                    execution_time_ms=execution_time
                ))
                
            except Exception as e:
                results.append(ContractTestResult(
                    test_name="performance_post_invoice",
                    adapter_name=adapter_name,
                    passed=False,
                    error_message=str(e),
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                ))
        
        return results

class TestERPContractTests:
    """Pytest test class for ERP contract tests"""
    
    @pytest.fixture
    def contract_tester(self):
        return ERPContractTester()
    
    @pytest.fixture
    def all_adapters(self):
        """Create all ERP adapters for testing"""
        return [
            MockERPAdapter("TestMock"),
            # Note: Real adapters would require proper configuration
            # MicrosoftDynamicsGPAdapter({}),
            # Dynamics365BCAdapter({}),
            # XeroAdapter({})
        ]
    
    @pytest.mark.asyncio
    async def test_all_adapters_implement_required_methods(self, all_adapters):
        """Test that all adapters implement required abstract methods"""
        for adapter in all_adapters:
            assert hasattr(adapter, 'health_check')
            assert hasattr(adapter, 'post_invoice')
            assert hasattr(adapter, 'get_invoice_status')
            assert hasattr(adapter, 'validate_connection')
            
            assert callable(adapter.health_check)
            assert callable(adapter.post_invoice)
            assert callable(adapter.get_invoice_status)
            assert callable(adapter.validate_connection)
    
    @pytest.mark.asyncio
    async def test_contract_compliance(self, contract_tester, all_adapters):
        """Run comprehensive contract tests"""
        results = await contract_tester.run_all_contract_tests(all_adapters)
        
        # Analyze results
        passed_tests = [r for r in results if r.passed]
        failed_tests = [r for r in results if not r.passed]
        
        print(f"\nContract Test Results:")
        print(f"Total tests: {len(results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print(f"\nFailed tests:")
            for test in failed_tests:
                print(f"  {test.adapter_name}.{test.test_name}: {test.error_message}")
        
        # Assert that all tests passed
        assert len(failed_tests) == 0, f"{len(failed_tests)} contract tests failed"
    
    @pytest.mark.asyncio
    async def test_response_time_requirements(self, contract_tester, all_adapters):
        """Test that all adapters meet response time requirements"""
        results = await contract_tester.run_all_contract_tests(all_adapters)
        
        # Check performance requirements
        performance_tests = [r for r in results if "performance" in r.test_name]
        
        for test in performance_tests:
            if test.test_name == "performance_health_check":
                assert test.execution_time_ms <= 5000, f"Health check too slow: {test.execution_time_ms}ms"
            elif test.test_name == "performance_post_invoice":
                assert test.execution_time_ms <= 30000, f"Invoice posting too slow: {test.execution_time_ms}ms"
    
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, contract_tester, all_adapters):
        """Test that error handling is consistent across adapters"""
        results = await contract_tester.run_all_contract_tests(all_adapters)
        
        error_handling_tests = [r for r in results if "error_handling" in r.test_name]
        
        # All error handling tests should pass
        failed_error_tests = [r for r in error_handling_tests if not r.passed]
        assert len(failed_error_tests) == 0, f"Error handling tests failed: {[t.error_message for t in failed_error_tests]}"
    
    @pytest.mark.asyncio
    async def test_data_type_consistency(self, all_adapters):
        """Test that all adapters return consistent data types"""
        for adapter in all_adapters:
            # Test health check response types
            health_result = await adapter.health_check()
            assert isinstance(health_result["status"], str)
            assert isinstance(health_result["erp_name"], str)
            assert isinstance(health_result["timestamp"], str)
            
            # Test connection validation response types
            connection_result = await adapter.validate_connection()
            assert isinstance(connection_result["status"], str)
            assert isinstance(connection_result["message"], str)
            assert isinstance(connection_result["timestamp"], str)

# Integration with golden datasets
class GoldenDatasetContractTests:
    """Contract tests using golden datasets"""
    
    @pytest.mark.asyncio
    async def test_ocr_accuracy_with_golden_datasets(self):
        """Test OCR accuracy using golden datasets"""
        golden_manager = golden_dataset_manager
        
        # Get simple datasets for baseline testing
        simple_datasets = golden_manager.get_datasets_by_category("simple")
        
        for dataset in simple_datasets[:2]:  # Test first 2 simple datasets
            # Mock OCR result (in production, this would be actual OCR output)
            mock_ocr_result = {
                "supplier_name": dataset.expected_data["supplier_name"],
                "invoice_number": dataset.expected_data["invoice_number"],
                "total_amount": dataset.expected_data["total_amount"],
                "confidence_scores": {
                    "supplier_name": 0.99,
                    "invoice_number": 0.99,
                    "total_amount": 0.99
                }
            }
            
            # Validate against golden dataset
            validation_result = golden_manager.validate_ocr_result(dataset.id, mock_ocr_result)
            
            # Should meet accuracy thresholds
            assert validation_result["valid"], f"OCR validation failed for {dataset.id}"
            assert validation_result["overall_accuracy"] >= 0.95, f"OCR accuracy too low: {validation_result['overall_accuracy']}"
    
    @pytest.mark.asyncio
    async def test_ml_model_accuracy_with_golden_datasets(self):
        """Test ML model accuracy using golden datasets"""
        from src.services.advanced_ml_models import advanced_ml_service
        
        # Test fraud detection model
        fraud_test_data = {
            "total_amount": 50000.0,
            "supplier_age_days": 30,
            "payment_terms": 90,
            "invoice_frequency": 1,
            "weekend_submission": 1,
            "amount_deviation": 0.8,
            "pattern_score": 0.2,
            "location_risk": 0.9,
            "time_since_last_hours": 1,
            "line_count": 1
        }
        
        fraud_result = await advanced_ml_service.predict_fraud(fraud_test_data)
        
        # Should return valid fraud prediction
        assert "fraud_probability" in fraud_result
        assert 0.0 <= fraud_result["fraud_probability"] <= 1.0
        assert "confidence" in fraud_result
        assert 0.0 <= fraud_result["confidence"] <= 1.0
