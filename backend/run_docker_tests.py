#!/usr/bin/env python3
"""
Docker-based test runner for the AI ERP SaaS application
Runs comprehensive tests using Docker containers
"""
import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class DockerTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.test_results = {}
        
    def run_command(self, command, cwd=None, capture_output=True):
        """Run a shell command and return the result"""
        print(f"Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"Command timed out: {command}")
            return None
        except Exception as e:
            print(f"Error running command: {e}")
            return None
    
    def check_docker_available(self):
        """Check if Docker and Docker Compose are available"""
        print("=== Checking Docker Availability ===")
        
        # Check Docker
        docker_result = self.run_command("docker --version")
        if not docker_result or docker_result.returncode != 0:
            print("❌ Docker is not available")
            return False
        print(f"✅ Docker: {docker_result.stdout.strip()}")
        
        # Check Docker Compose
        compose_result = self.run_command("docker-compose --version")
        if not compose_result or compose_result.returncode != 0:
            print("❌ Docker Compose is not available")
            return False
        print(f"✅ Docker Compose: {compose_result.stdout.strip()}")
        
        return True
    
    def build_test_images(self):
        """Build Docker images for testing"""
        print("\n=== Building Test Images ===")
        
        # Build OCR service
        print("Building OCR service...")
        ocr_result = self.run_command(
            "docker build -t ai-erp-ocr-test ./ocr-service",
            cwd=self.project_root
        )
        if not ocr_result or ocr_result.returncode != 0:
            print("❌ Failed to build OCR service")
            return False
        print("✅ OCR service built successfully")
        
        # Build backend
        print("Building backend...")
        backend_result = self.run_command(
            "docker build -t ai-erp-backend-test ./backend",
            cwd=self.project_root
        )
        if not backend_result or backend_result.returncode != 0:
            print("❌ Failed to build backend")
            return False
        print("✅ Backend built successfully")
        
        return True
    
    def start_test_services(self):
        """Start test services using Docker Compose"""
        print("\n=== Starting Test Services ===")
        
        # Start services
        start_result = self.run_command(
            "docker-compose -f docker-compose.test.yml up -d postgres-test redis-test ocr-service-test",
            cwd=self.project_root
        )
        if not start_result or start_result.returncode != 0:
            print("❌ Failed to start test services")
            return False
        
        print("✅ Test services started")
        
        # Wait for services to be healthy
        print("Waiting for services to be healthy...")
        time.sleep(30)
        
        # Check service health
        health_result = self.run_command(
            "docker-compose -f docker-compose.test.yml ps",
            cwd=self.project_root
        )
        if health_result:
            print("Service status:")
            print(health_result.stdout)
        
        return True
    
    def run_backend_tests(self):
        """Run backend tests in Docker container"""
        print("\n=== Running Backend Tests ===")
        
        # Run backend tests
        test_result = self.run_command(
            "docker-compose -f docker-compose.test.yml run --rm backend-test",
            cwd=self.project_root
        )
        
        if test_result and test_result.returncode == 0:
            print("✅ Backend tests passed")
            self.test_results['backend'] = {
                'status': 'passed',
                'output': test_result.stdout
            }
            return True
        else:
            print("❌ Backend tests failed")
            self.test_results['backend'] = {
                'status': 'failed',
                'output': test_result.stdout if test_result else "No output",
                'error': test_result.stderr if test_result else "Unknown error"
            }
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("\n=== Running Integration Tests ===")
        
        # Run our comprehensive integration tests
        integration_result = self.run_command(
            "python test_comprehensive_integration.py",
            cwd=self.backend_dir
        )
        
        if integration_result and integration_result.returncode == 0:
            print("✅ Integration tests passed")
            self.test_results['integration'] = {
                'status': 'passed',
                'output': integration_result.stdout
            }
            return True
        else:
            print("❌ Integration tests failed")
            self.test_results['integration'] = {
                'status': 'failed',
                'output': integration_result.stdout if integration_result else "No output",
                'error': integration_result.stderr if integration_result else "Unknown error"
            }
            return False
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("\n=== Running Performance Tests ===")
        
        # Create a simple performance test
        perf_test = """
import time
import asyncio
from services.simple_ocr import SimpleOCRService

async def performance_test():
    ocr_service = SimpleOCRService()
    start_time = time.time()
    
    # Run multiple OCR operations
    tasks = []
    for i in range(10):
        task = ocr_service.extract_invoice(f"test_{i}.pdf", f"company_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / len(results)
    
    print(f"Processed {len(results)} invoices in {total_time:.2f}s")
    print(f"Average time per invoice: {avg_time:.3f}s")
    
    # Performance criteria
    assert total_time < 5.0, f"Total time too slow: {total_time:.2f}s"
    assert avg_time < 0.5, f"Average time too slow: {avg_time:.3f}s"
    
    print("✅ Performance tests passed")
    return True

if __name__ == "__main__":
    import sys
    sys.path.insert(0, 'src')
    success = asyncio.run(performance_test())
    sys.exit(0 if success else 1)
"""
        
        # Write and run performance test
        perf_file = self.backend_dir / "test_performance_docker.py"
        perf_file.write_text(perf_test)
        
        perf_result = self.run_command(
            "python test_performance_docker.py",
            cwd=self.backend_dir
        )
        
        # Clean up
        perf_file.unlink()
        
        if perf_result and perf_result.returncode == 0:
            print("✅ Performance tests passed")
            self.test_results['performance'] = {
                'status': 'passed',
                'output': perf_result.stdout
            }
            return True
        else:
            print("❌ Performance tests failed")
            self.test_results['performance'] = {
                'status': 'failed',
                'output': perf_result.stdout if perf_result else "No output",
                'error': perf_result.stderr if perf_result else "Unknown error"
            }
            return False
    
    def cleanup_test_services(self):
        """Clean up test services"""
        print("\n=== Cleaning Up Test Services ===")
        
        # Stop and remove containers
        cleanup_result = self.run_command(
            "docker-compose -f docker-compose.test.yml down -v",
            cwd=self.project_root
        )
        
        if cleanup_result and cleanup_result.returncode == 0:
            print("✅ Test services cleaned up")
        else:
            print("⚠️ Cleanup may have failed")
    
    def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n=== Test Report ===")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        print(f"Total test suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            print(f"{status_icon} {test_name.title()}: {result['status'].upper()}")
        
        # Save report to file
        report_file = self.backend_dir / "test_report.json"
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'results': self.test_results
        }
        
        report_file.write_text(json.dumps(report_data, indent=2))
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Docker-based Test Suite")
        print("=" * 50)
        
        try:
            # Check prerequisites
            if not self.check_docker_available():
                return False
            
            # Build images
            if not self.build_test_images():
                return False
            
            # Start services
            if not self.start_test_services():
                return False
            
            # Run tests
            backend_success = self.run_backend_tests()
            integration_success = self.run_integration_tests()
            performance_success = self.run_performance_tests()
            
            # Generate report
            overall_success = self.generate_test_report()
            
            return overall_success
            
        finally:
            # Always cleanup
            self.cleanup_test_services()

def main():
    """Main entry point"""
    runner = DockerTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()









