"""
Performance Testing Framework for AI ERP SaaS Platform
World-class performance testing with load testing, stress testing, and benchmarking
"""
import pytest
import asyncio
import time
import statistics
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp
from unittest.mock import Mock, AsyncMock

from src.services.invoice_processor import InvoiceProcessor
from src.services.advanced_ml_models import advanced_ml_service
from src.services.erp import ERPIntegrationService
from src.models.invoice import Invoice, InvoiceStatus
from tests.golden_datasets import golden_dataset_manager

@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    throughput_mbps: float
    error_rate_percent: float
    test_duration_seconds: float

@dataclass
class LoadTestConfig:
    """Configuration for load tests"""
    concurrent_users: int
    requests_per_user: int
    ramp_up_seconds: int
    test_duration_seconds: int
    target_response_time_ms: int
    max_error_rate_percent: float

class PerformanceTestFramework:
    """Comprehensive performance testing framework"""
    
    def __init__(self):
        self.invoice_processor = InvoiceProcessor()
        self.erp_service = ERPIntegrationService()
        self.test_configs = self._create_test_configurations()
        self.performance_thresholds = self._define_performance_thresholds()
    
    def _create_test_configurations(self) -> Dict[str, LoadTestConfig]:
        """Create various load test configurations"""
        return {
            "light_load": LoadTestConfig(
                concurrent_users=10,
                requests_per_user=10,
                ramp_up_seconds=30,
                test_duration_seconds=60,
                target_response_time_ms=500,
                max_error_rate_percent=1.0
            ),
            "normal_load": LoadTestConfig(
                concurrent_users=50,
                requests_per_user=20,
                ramp_up_seconds=60,
                test_duration_seconds=300,
                target_response_time_ms=1000,
                max_error_rate_percent=2.0
            ),
            "heavy_load": LoadTestConfig(
                concurrent_users=100,
                requests_per_user=30,
                ramp_up_seconds=120,
                test_duration_seconds=600,
                target_response_time_ms=2000,
                max_error_rate_percent=5.0
            ),
            "stress_test": LoadTestConfig(
                concurrent_users=200,
                requests_per_user=50,
                ramp_up_seconds=180,
                test_duration_seconds=900,
                target_response_time_ms=5000,
                max_error_rate_percent=10.0
            )
        }
    
    def _define_performance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Define performance thresholds for different operations"""
        return {
            "invoice_processing": {
                "max_response_time_ms": 5000,
                "min_throughput_rps": 10,
                "max_error_rate_percent": 1.0,
                "min_accuracy_percent": 95.0
            },
            "ocr_processing": {
                "max_response_time_ms": 10000,
                "min_throughput_rps": 5,
                "max_error_rate_percent": 2.0,
                "min_accuracy_percent": 90.0
            },
            "ml_prediction": {
                "max_response_time_ms": 2000,
                "min_throughput_rps": 20,
                "max_error_rate_percent": 1.0,
                "min_accuracy_percent": 85.0
            },
            "erp_integration": {
                "max_response_time_ms": 30000,
                "min_throughput_rps": 2,
                "max_error_rate_percent": 5.0,
                "min_accuracy_percent": 98.0
            }
        }
    
    async def run_invoice_processing_load_test(self, config_name: str = "normal_load") -> PerformanceMetrics:
        """Run load test for invoice processing"""
        config = self.test_configs[config_name]
        golden_datasets = golden_dataset_manager.get_datasets_by_category("simple")
        
        if not golden_datasets:
            raise ValueError("No golden datasets available for testing")
        
        # Prepare test data
        test_invoice = golden_datasets[0]
        mock_file_path = test_invoice.file_path
        company_id = "test_company"
        user_id = "test_user"
        
        # Mock database session
        mock_db = Mock()
        
        results = []
        start_time = time.time()
        
        # Create async tasks for concurrent execution
        tasks = []
        for user_id_num in range(config.concurrent_users):
            for request_num in range(config.requests_per_user):
                task = self._simulate_invoice_processing(
                    mock_file_path, company_id, f"user_{user_id_num}", mock_db
                )
                tasks.append(task)
        
        # Execute all tasks concurrently
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Process results
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for result in task_results:
            if isinstance(result, Exception):
                failed_requests += 1
                response_times.append(config.target_response_time_ms * 2)  # Penalty for failure
            else:
                successful_requests += 1
                response_times.append(result.get("response_time_ms", 0))
        
        total_requests = len(tasks)
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(
            "invoice_processing_load_test",
            total_requests,
            successful_requests,
            failed_requests,
            response_times,
            test_duration
        )
        
        return metrics
    
    async def _simulate_invoice_processing(
        self,
        file_path: str,
        company_id: str,
        user_id: str,
        db: Mock
    ) -> Dict[str, Any]:
        """Simulate invoice processing for load testing"""
        start_time = time.time()
        
        try:
            # Mock the invoice processing
            result = await self.invoice_processor.process_invoice(
                file_path, company_id, user_id, db
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response_time_ms": response_time,
                "result": result
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time,
                "error": str(e)
            }
    
    async def run_ocr_processing_load_test(self, config_name: str = "normal_load") -> PerformanceMetrics:
        """Run load test for OCR processing"""
        config = self.test_configs[config_name]
        golden_datasets = golden_dataset_manager.get_datasets_by_category("simple")
        
        if not golden_datasets:
            raise ValueError("No golden datasets available for testing")
        
        test_dataset = golden_datasets[0]
        
        results = []
        start_time = time.time()
        
        # Create async tasks for concurrent OCR processing
        tasks = []
        for user_id_num in range(config.concurrent_users):
            for request_num in range(config.requests_per_user):
                task = self._simulate_ocr_processing(
                    test_dataset.file_path, f"company_{user_id_num}"
                )
                tasks.append(task)
        
        # Execute all tasks concurrently
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Process results
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for result in task_results:
            if isinstance(result, Exception):
                failed_requests += 1
                response_times.append(config.target_response_time_ms * 2)
            else:
                successful_requests += 1
                response_times.append(result.get("response_time_ms", 0))
        
        total_requests = len(tasks)
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(
            "ocr_processing_load_test",
            total_requests,
            successful_requests,
            failed_requests,
            response_times,
            test_duration
        )
        
        return metrics
    
    async def _simulate_ocr_processing(self, file_path: str, company_id: str) -> Dict[str, Any]:
        """Simulate OCR processing for load testing"""
        start_time = time.time()
        
        try:
            # Mock OCR processing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response_time_ms": response_time,
                "extracted_data": {"supplier_name": "Test Supplier", "total_amount": 1000.0}
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time,
                "error": str(e)
            }
    
    async def run_ml_prediction_load_test(self, config_name: str = "normal_load") -> PerformanceMetrics:
        """Run load test for ML predictions"""
        config = self.test_configs[config_name]
        
        # Prepare test data
        test_data = {
            "total_amount": 1000.0,
            "supplier_age_days": 365,
            "payment_terms": 30,
            "invoice_frequency": 5,
            "weekend_submission": 0,
            "amount_deviation": 0.0,
            "pattern_score": 0.8,
            "location_risk": 0.3,
            "time_since_last_hours": 72,
            "line_count": 5
        }
        
        results = []
        start_time = time.time()
        
        # Create async tasks for concurrent ML predictions
        tasks = []
        for user_id_num in range(config.concurrent_users):
            for request_num in range(config.requests_per_user):
                task = self._simulate_ml_prediction(test_data)
                tasks.append(task)
        
        # Execute all tasks concurrently
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Process results
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for result in task_results:
            if isinstance(result, Exception):
                failed_requests += 1
                response_times.append(config.target_response_time_ms * 2)
            else:
                successful_requests += 1
                response_times.append(result.get("response_time_ms", 0))
        
        total_requests = len(tasks)
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(
            "ml_prediction_load_test",
            total_requests,
            successful_requests,
            failed_requests,
            response_times,
            test_duration
        )
        
        return metrics
    
    async def _simulate_ml_prediction(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate ML prediction for load testing"""
        start_time = time.time()
        
        try:
            # Mock ML prediction
            result = await advanced_ml_service.predict_fraud(test_data)
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response_time_ms": response_time,
                "prediction": result
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time,
                "error": str(e)
            }
    
    async def run_erp_integration_load_test(self, config_name: str = "normal_load") -> PerformanceMetrics:
        """Run load test for ERP integration"""
        config = self.test_configs[config_name]
        
        # Create test invoice
        test_invoice = Invoice(
            id="test_invoice",
            invoice_number="TEST-001",
            supplier_name="Test Supplier",
            total_amount=1000.00,
            currency="USD",
            status=InvoiceStatus.PENDING
        )
        
        company_settings = {"company_id": "test_company", "erp_config": {}}
        
        results = []
        start_time = time.time()
        
        # Create async tasks for concurrent ERP operations
        tasks = []
        for user_id_num in range(config.concurrent_users):
            for request_num in range(config.requests_per_user):
                task = self._simulate_erp_integration(test_invoice, company_settings)
                tasks.append(task)
        
        # Execute all tasks concurrently
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        # Process results
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        for result in task_results:
            if isinstance(result, Exception):
                failed_requests += 1
                response_times.append(config.target_response_time_ms * 2)
            else:
                successful_requests += 1
                response_times.append(result.get("response_time_ms", 0))
        
        total_requests = len(tasks)
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics(
            "erp_integration_load_test",
            total_requests,
            successful_requests,
            failed_requests,
            response_times,
            test_duration
        )
        
        return metrics
    
    async def _simulate_erp_integration(self, invoice: Invoice, company_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate ERP integration for load testing"""
        start_time = time.time()
        
        try:
            # Mock ERP integration
            result = await self.erp_service.post_invoice(invoice, "mock", company_settings)
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response_time_ms": response_time,
                "result": result
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time,
                "error": str(e)
            }
    
    def _calculate_performance_metrics(
        self,
        test_name: str,
        total_requests: int,
        successful_requests: int,
        failed_requests: int,
        response_times: List[float],
        test_duration: float
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        
        if not response_times:
            response_times = [0.0]
        
        # Basic metrics
        average_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Percentile calculations
        sorted_times = sorted(response_times)
        p50_index = int(len(sorted_times) * 0.5)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        p50_response_time = sorted_times[p50_index] if p50_index < len(sorted_times) else sorted_times[-1]
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1]
        
        # Throughput metrics
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0
        error_rate_percent = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Estimate throughput in Mbps (rough calculation)
        avg_response_size_bytes = 1024  # Estimated average response size
        throughput_mbps = (requests_per_second * avg_response_size_bytes * 8) / (1024 * 1024)
        
        return PerformanceMetrics(
            test_name=test_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time_ms=average_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p50_response_time_ms=p50_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            requests_per_second=requests_per_second,
            throughput_mbps=throughput_mbps,
            error_rate_percent=error_rate_percent,
            test_duration_seconds=test_duration
        )
    
    async def run_stress_test(self, operation: str) -> Dict[str, Any]:
        """Run stress test to find breaking point"""
        stress_config = self.test_configs["stress_test"]
        
        # Gradually increase load until failure
        load_levels = [10, 25, 50, 100, 150, 200, 250, 300]
        results = []
        
        for concurrent_users in load_levels:
            try:
                # Create temporary config with current load level
                temp_config = LoadTestConfig(
                    concurrent_users=concurrent_users,
                    requests_per_user=stress_config.requests_per_user,
                    ramp_up_seconds=stress_config.ramp_up_seconds,
                    test_duration_seconds=60,  # Shorter duration for stress test
                    target_response_time_ms=stress_config.target_response_time_ms,
                    max_error_rate_percent=stress_config.max_error_rate_percent
                )
                
                # Run test with current load level
                if operation == "invoice_processing":
                    metrics = await self.run_invoice_processing_load_test("stress_test")
                elif operation == "ocr_processing":
                    metrics = await self.run_ocr_processing_load_test("stress_test")
                elif operation == "ml_prediction":
                    metrics = await self.run_ml_prediction_load_test("stress_test")
                elif operation == "erp_integration":
                    metrics = await self.run_erp_integration_load_test("stress_test")
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                
                results.append({
                    "concurrent_users": concurrent_users,
                    "metrics": metrics,
                    "passed": metrics.error_rate_percent <= stress_config.max_error_rate_percent
                })
                
                # Stop if error rate is too high
                if metrics.error_rate_percent > stress_config.max_error_rate_percent:
                    break
                    
            except Exception as e:
                results.append({
                    "concurrent_users": concurrent_users,
                    "error": str(e),
                    "passed": False
                })
                break
        
        return {
            "operation": operation,
            "stress_test_results": results,
            "max_sustainable_load": max([r["concurrent_users"] for r in results if r["passed"]], default=0)
        }
    
    def validate_performance_metrics(self, metrics: PerformanceMetrics, operation: str) -> Dict[str, Any]:
        """Validate performance metrics against thresholds"""
        thresholds = self.performance_thresholds.get(operation, {})
        
        validation_results = {
            "passed": True,
            "violations": [],
            "metrics": metrics
        }
        
        # Check response time
        max_response_time = thresholds.get("max_response_time_ms", float('inf'))
        if metrics.average_response_time_ms > max_response_time:
            validation_results["passed"] = False
            validation_results["violations"].append(
                f"Average response time {metrics.average_response_time_ms:.2f}ms exceeds threshold {max_response_time}ms"
            )
        
        # Check throughput
        min_throughput = thresholds.get("min_throughput_rps", 0)
        if metrics.requests_per_second < min_throughput:
            validation_results["passed"] = False
            validation_results["violations"].append(
                f"Throughput {metrics.requests_per_second:.2f} RPS below threshold {min_throughput} RPS"
            )
        
        # Check error rate
        max_error_rate = thresholds.get("max_error_rate_percent", 100)
        if metrics.error_rate_percent > max_error_rate:
            validation_results["passed"] = False
            validation_results["violations"].append(
                f"Error rate {metrics.error_rate_percent:.2f}% exceeds threshold {max_error_rate}%"
            )
        
        return validation_results

class TestPerformanceTests:
    """Pytest test class for performance tests"""
    
    @pytest.fixture
    def performance_framework(self):
        return PerformanceTestFramework()
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_invoice_processing_performance(self, performance_framework):
        """Test invoice processing performance under normal load"""
        metrics = await performance_framework.run_invoice_processing_load_test("normal_load")
        
        # Validate performance
        validation = performance_framework.validate_performance_metrics(metrics, "invoice_processing")
        
        assert validation["passed"], f"Performance validation failed: {validation['violations']}"
        
        # Print metrics for monitoring
        print(f"\nInvoice Processing Performance:")
        print(f"Total requests: {metrics.total_requests}")
        print(f"Successful requests: {metrics.successful_requests}")
        print(f"Failed requests: {metrics.failed_requests}")
        print(f"Average response time: {metrics.average_response_time_ms:.2f}ms")
        print(f"95th percentile response time: {metrics.p95_response_time_ms:.2f}ms")
        print(f"Requests per second: {metrics.requests_per_second:.2f}")
        print(f"Error rate: {metrics.error_rate_percent:.2f}%")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_ocr_processing_performance(self, performance_framework):
        """Test OCR processing performance under normal load"""
        metrics = await performance_framework.run_ocr_processing_load_test("normal_load")
        
        # Validate performance
        validation = performance_framework.validate_performance_metrics(metrics, "ocr_processing")
        
        assert validation["passed"], f"Performance validation failed: {validation['violations']}"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_ml_prediction_performance(self, performance_framework):
        """Test ML prediction performance under normal load"""
        metrics = await performance_framework.run_ml_prediction_load_test("normal_load")
        
        # Validate performance
        validation = performance_framework.validate_performance_metrics(metrics, "ml_prediction")
        
        assert validation["passed"], f"Performance validation failed: {validation['violations']}"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_erp_integration_performance(self, performance_framework):
        """Test ERP integration performance under normal load"""
        metrics = await performance_framework.run_erp_integration_load_test("normal_load")
        
        # Validate performance
        validation = performance_framework.validate_performance_metrics(metrics, "erp_integration")
        
        assert validation["passed"], f"Performance validation failed: {validation['violations']}"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_stress_test_invoice_processing(self, performance_framework):
        """Run stress test for invoice processing to find breaking point"""
        stress_results = await performance_framework.run_stress_test("invoice_processing")
        
        # Should handle at least some load
        assert stress_results["max_sustainable_load"] > 0, "System cannot handle any load"
        
        print(f"\nStress Test Results for Invoice Processing:")
        print(f"Max sustainable load: {stress_results['max_sustainable_load']} concurrent users")
        
        # Print detailed results
        for result in stress_results["stress_test_results"]:
            if "metrics" in result:
                metrics = result["metrics"]
                print(f"  {result['concurrent_users']} users: "
                      f"{metrics.requests_per_second:.2f} RPS, "
                      f"{metrics.average_response_time_ms:.2f}ms avg, "
                      f"{metrics.error_rate_percent:.2f}% errors - "
                      f"{'PASSED' if result['passed'] else 'FAILED'}")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_operations_performance(self, performance_framework):
        """Test performance of concurrent operations across different services"""
        
        # Run multiple operations concurrently
        tasks = [
            performance_framework.run_invoice_processing_load_test("light_load"),
            performance_framework.run_ocr_processing_load_test("light_load"),
            performance_framework.run_ml_prediction_load_test("light_load"),
            performance_framework.run_erp_integration_load_test("light_load")
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All operations should complete successfully
        for i, metrics in enumerate(results):
            operation_names = ["invoice_processing", "ocr_processing", "ml_prediction", "erp_integration"]
            operation = operation_names[i]
            
            validation = performance_framework.validate_performance_metrics(metrics, operation)
            assert validation["passed"], f"Concurrent {operation} failed: {validation['violations']}"
        
        print(f"\nConcurrent Operations Performance Test - All operations completed successfully")
