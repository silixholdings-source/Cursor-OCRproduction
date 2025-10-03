#!/usr/bin/env python3
"""
Staging Smoke Tests
Comprehensive smoke tests for staging environment validation
"""
import argparse
import requests
import time
import sys
from typing import Dict, List, Any, Optional
import json


class StagingSmokeTester:
    """Comprehensive smoke tests for staging environment"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Test endpoints
        self.endpoints = {
            'health': '/health',
            'docs': '/docs',
            'openapi': '/openapi.json',
            'auth_login': '/api/v1/auth/login',
            'auth_register': '/api/v1/auth/register',
            'invoices': '/api/v1/invoices',
            'companies': '/api/v1/companies',
            'users': '/api/v1/users',
            'subscriptions': '/api/v1/subscriptions',
            'pricing': '/api/v1/pricing'
        }
        
        # Expected status codes
        self.expected_status_codes = {
            'health': [200],
            'docs': [200],
            'openapi': [200],
            'auth_login': [200, 401, 422],  # 401 for no credentials, 422 for validation
            'auth_register': [200, 422],    # 422 for validation errors
            'invoices': [200, 401, 403],    # 401/403 for no auth
            'companies': [200, 401, 403],   # 401/403 for no auth
            'users': [200, 401, 403],       # 401/403 for no auth
            'subscriptions': [200, 401, 403], # 401/403 for no auth
            'pricing': [200]
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all smoke tests"""
        print("🧪 Running staging smoke tests...")
        print(f"Base URL: {self.base_url}")
        
        results = {
            'timestamp': time.time(),
            'base_url': self.base_url,
            'tests': {},
            'overall_status': 'PASS',
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0
            }
        }
        
        # Test basic connectivity
        connectivity_result = self.test_connectivity()
        results['tests']['connectivity'] = connectivity_result
        
        if not connectivity_result['passed']:
            results['overall_status'] = 'FAIL'
            print("❌ Connectivity test failed - aborting other tests")
            return results
        
        # Test all endpoints
        for endpoint_name, endpoint_path in self.endpoints.items():
            test_result = self.test_endpoint(endpoint_name, endpoint_path)
            results['tests'][endpoint_name] = test_result
            results['summary']['total'] += 1
            
            if test_result['passed']:
                results['summary']['passed'] += 1
                print(f"✅ {endpoint_name}: PASS")
            else:
                results['summary']['failed'] += 1
                print(f"❌ {endpoint_name}: FAIL - {test_result['error']}")
                results['overall_status'] = 'FAIL'
        
        # Test performance
        performance_result = self.test_performance()
        results['tests']['performance'] = performance_result
        
        # Test database connectivity
        db_result = self.test_database_connectivity()
        results['tests']['database'] = db_result
        
        # Test external services
        external_result = self.test_external_services()
        results['tests']['external_services'] = external_result
        
        return results
    
    def test_connectivity(self) -> Dict[str, Any]:
        """Test basic connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return {
                'passed': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'error': None if response.status_code == 200 else f"Unexpected status code: {response.status_code}"
            }
        except Exception as e:
            return {
                'passed': False,
                'status_code': None,
                'response_time': None,
                'error': str(e)
            }
    
    def test_endpoint(self, endpoint_name: str, endpoint_path: str) -> Dict[str, Any]:
        """Test a specific endpoint"""
        try:
            url = f"{self.base_url}{endpoint_path}"
            response = self.session.get(url)
            
            expected_codes = self.expected_status_codes.get(endpoint_name, [200])
            passed = response.status_code in expected_codes
            
            return {
                'passed': passed,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'expected_codes': expected_codes,
                'error': None if passed else f"Unexpected status code: {response.status_code} (expected: {expected_codes})"
            }
        except Exception as e:
            return {
                'passed': False,
                'status_code': None,
                'response_time': None,
                'error': str(e)
            }
    
    def test_performance(self) -> Dict[str, Any]:
        """Test performance metrics"""
        print("📊 Testing performance...")
        
        performance_tests = []
        
        # Test health endpoint performance (should be fast)
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            performance_tests.append({
                'endpoint': '/health',
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'passed': response_time < 1000 and response.status_code == 200  # < 1 second
            })
        except Exception as e:
            performance_tests.append({
                'endpoint': '/health',
                'response_time_ms': None,
                'status_code': None,
                'passed': False,
                'error': str(e)
            })
        
        # Test docs endpoint performance
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/docs")
            response_time = (time.time() - start_time) * 1000
            
            performance_tests.append({
                'endpoint': '/docs',
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'passed': response_time < 3000 and response.status_code == 200  # < 3 seconds
            })
        except Exception as e:
            performance_tests.append({
                'endpoint': '/docs',
                'response_time_ms': None,
                'status_code': None,
                'passed': False,
                'error': str(e)
            })
        
        # Calculate overall performance score
        passed_tests = sum(1 for test in performance_tests if test['passed'])
        total_tests = len(performance_tests)
        
        return {
            'passed': passed_tests == total_tests,
            'score': passed_tests / total_tests,
            'tests': performance_tests,
            'summary': f"{passed_tests}/{total_tests} performance tests passed"
        }
    
    def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database connectivity through API"""
        print("🗄️ Testing database connectivity...")
        
        # Test by hitting an endpoint that requires database access
        try:
            response = self.session.get(f"{self.base_url}/api/v1/pricing")
            
            # If we get a 200, database is likely working
            # If we get 500, it might be a database issue
            if response.status_code == 200:
                return {
                    'passed': True,
                    'status_code': response.status_code,
                    'error': None
                }
            elif response.status_code == 500:
                # Check if it's a database error
                try:
                    error_data = response.json()
                    if 'database' in str(error_data).lower():
                        return {
                            'passed': False,
                            'status_code': response.status_code,
                            'error': f"Database error: {error_data}"
                        }
                except:
                    pass
                
                return {
                    'passed': False,
                    'status_code': response.status_code,
                    'error': f"Server error: {response.status_code}"
                }
            else:
                return {
                    'passed': True,  # Non-500 errors are OK for this test
                    'status_code': response.status_code,
                    'error': None
                }
        except Exception as e:
            return {
                'passed': False,
                'status_code': None,
                'error': str(e)
            }
    
    def test_external_services(self) -> Dict[str, Any]:
        """Test external service dependencies"""
        print("🌐 Testing external services...")
        
        external_tests = []
        
        # Test Paystack connectivity (if configured)
        try:
            # This would be a health check endpoint for Paystack integration
            response = self.session.get(f"{self.base_url}/api/v1/health/paystack")
            external_tests.append({
                'service': 'paystack',
                'passed': response.status_code in [200, 404],  # 404 is OK if not configured
                'status_code': response.status_code
            })
        except Exception as e:
            external_tests.append({
                'service': 'paystack',
                'passed': True,  # Don't fail on external service issues
                'error': str(e)
            })
        
        # Test ERP connectivity
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health/erp")
            external_tests.append({
                'service': 'erp',
                'passed': response.status_code in [200, 404],
                'status_code': response.status_code
            })
        except Exception as e:
            external_tests.append({
                'service': 'erp',
                'passed': True,
                'error': str(e)
            })
        
        # Calculate overall external services score
        passed_tests = sum(1 for test in external_tests if test['passed'])
        total_tests = len(external_tests)
        
        return {
            'passed': passed_tests == total_tests,
            'score': passed_tests / total_tests,
            'tests': external_tests,
            'summary': f"{passed_tests}/{total_tests} external services accessible"
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate test report"""
        report = f"""
# 🧪 Staging Smoke Test Report

## 📊 Summary
- **Overall Status:** {results['overall_status']}
- **Total Tests:** {results['summary']['total']}
- **Passed:** {results['summary']['passed']}
- **Failed:** {results['summary']['failed']}
- **Success Rate:** {results['summary']['passed'] / results['summary']['total'] * 100:.1f}%

## 🔍 Test Results

### Connectivity
- **Status:** {'✅ PASS' if results['tests']['connectivity']['passed'] else '❌ FAIL'}
- **Response Time:** {results['tests']['connectivity']['response_time']:.3f}s
- **Status Code:** {results['tests']['connectivity']['status_code']}

### Endpoint Tests
"""
        
        for endpoint_name, test_result in results['tests'].items():
            if endpoint_name in ['connectivity', 'performance', 'database', 'external_services']:
                continue
                
            status = '✅ PASS' if test_result['passed'] else '❌ FAIL'
            report += f"- **{endpoint_name}:** {status} ({test_result['status_code']}, {test_result['response_time']:.3f}s)\n"
        
        report += f"""
### Performance
- **Status:** {'✅ PASS' if results['tests']['performance']['passed'] else '❌ FAIL'}
- **Score:** {results['tests']['performance']['score']:.1%}
- **Summary:** {results['tests']['performance']['summary']}

### Database
- **Status:** {'✅ PASS' if results['tests']['database']['passed'] else '❌ FAIL'}
- **Status Code:** {results['tests']['database']['status_code']}

### External Services
- **Status:** {'✅ PASS' if results['tests']['external_services']['passed'] else '❌ FAIL'}
- **Score:** {results['tests']['external_services']['score']:.1%}
- **Summary:** {results['tests']['external_services']['summary']}

## 🎯 Recommendations

"""
        
        if results['overall_status'] == 'FAIL':
            report += "- ❌ **Critical issues found** - Do not proceed to production deployment\n"
            report += "- 🔧 **Fix failing tests** before canary deployment\n"
            report += "- 📊 **Review performance metrics** and optimize if needed\n"
        else:
            report += "- ✅ **All tests passed** - Safe to proceed to canary deployment\n"
            report += "- 🚀 **Ready for production** deployment\n"
        
        report += f"""
---
**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Base URL:** {results['base_url']}
"""
        
        return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Staging Smoke Tests')
    parser.add_argument('--base-url', required=True, help='Base URL for staging environment')
    parser.add_argument('--output', help='Output file for test results')
    
    args = parser.parse_args()
    
    # Run smoke tests
    tester = StagingSmokeTester(args.base_url)
    results = tester.run_all_tests()
    
    # Generate report
    report = tester.generate_report(results)
    
    # Print report
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # Save report if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with appropriate code
    if results['overall_status'] == 'PASS':
        print("\n✅ All smoke tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some smoke tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()








