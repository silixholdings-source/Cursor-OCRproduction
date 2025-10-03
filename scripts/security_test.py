#!/usr/bin/env python3
"""
Security Testing Script for AI ERP SaaS Application
Runs comprehensive security tests including SAST, dependency scanning, and OWASP checks
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any

class SecurityTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.results = {}
        
    def run_command(self, command: List[str], cwd: Path = None) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit SAST scan"""
        print("🔍 Running Bandit SAST scan...")
        
        # Run Bandit scan
        exit_code, stdout, stderr = self.run_command([
            "bandit", "-r", "src/", "-f", "json", "-o", "bandit-results.json"
        ], cwd=self.backend_dir)
        
        # Also run with text output for console
        self.run_command([
            "bandit", "-r", "src/", "-f", "txt"
        ], cwd=self.backend_dir)
        
        return {
            "tool": "bandit",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "success": exit_code == 0
        }
    
    def run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety dependency scan"""
        print("🔍 Running Safety dependency scan...")
        
        exit_code, stdout, stderr = self.run_command([
            "safety", "check", "--json", "--output", "safety-results.json"
        ], cwd=self.backend_dir)
        
        # Also run with text output for console
        self.run_command([
            "safety", "check"
        ], cwd=self.backend_dir)
        
        return {
            "tool": "safety",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "success": exit_code == 0
        }
    
    def run_semgrep_scan(self) -> Dict[str, Any]:
        """Run Semgrep SAST scan"""
        print("🔍 Running Semgrep SAST scan...")
        
        exit_code, stdout, stderr = self.run_command([
            "semgrep", "--config=auto", "--json", "--output=semgrep-results.json"
        ])
        
        # Also run with text output for console
        self.run_command([
            "semgrep", "--config=auto"
        ])
        
        return {
            "tool": "semgrep",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "success": exit_code == 0
        }
    
    def run_snyk_scan(self) -> Dict[str, Any]:
        """Run Snyk dependency scan"""
        print("🔍 Running Snyk dependency scan...")
        
        exit_code, stdout, stderr = self.run_command([
            "snyk", "test", "--json-file-output=snyk-results.json"
        ])
        
        # Also run with text output for console
        self.run_command([
            "snyk", "test"
        ])
        
        return {
            "tool": "snyk",
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "success": exit_code == 0
        }
    
    def check_security_headers(self) -> Dict[str, Any]:
        """Check security headers configuration"""
        print("🔍 Checking security headers...")
        
        # Check if security headers are properly configured
        security_files = [
            "backend/src/core/security_headers.py",
            "web/next.config.js",
            "docker-compose.yml"
        ]
        
        issues = []
        for file_path in security_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                issues.append(f"Security configuration file missing: {file_path}")
        
        return {
            "tool": "security_headers",
            "issues": issues,
            "success": len(issues) == 0
        }
    
    def check_owasp_top10(self) -> Dict[str, Any]:
        """Check OWASP Top 10 vulnerabilities"""
        print("🔍 Checking OWASP Top 10 vulnerabilities...")
        
        issues = []
        
        # Check for common OWASP Top 10 issues
        owasp_checks = [
            {
                "name": "SQL Injection",
                "pattern": "f\"SELECT.*{.*}.*\"",
                "files": ["backend/src"]
            },
            {
                "name": "Cross-Site Scripting (XSS)",
                "pattern": "innerHTML|dangerouslySetInnerHTML",
                "files": ["web/src"]
            },
            {
                "name": "Broken Authentication",
                "pattern": "password.*=.*[\"'].*[\"']",
                "files": ["backend/src", "web/src"]
            },
            {
                "name": "Sensitive Data Exposure",
                "pattern": "console\.log.*password|console\.log.*token",
                "files": ["web/src", "mobile/src"]
            },
            {
                "name": "Security Misconfiguration",
                "pattern": "debug.*=.*True|DEBUG.*=.*True",
                "files": ["backend/src"]
            }
        ]
        
        for check in owasp_checks:
            # This is a simplified check - in practice, you'd use grep or similar
            issues.append(f"OWASP check '{check['name']}' - manual verification needed")
        
        return {
            "tool": "owasp_top10",
            "issues": issues,
            "success": len(issues) == 0
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        print("🚀 Starting comprehensive security testing...")
        print("=" * 60)
        
        tests = [
            self.run_bandit_scan,
            self.run_safety_scan,
            self.run_semgrep_scan,
            self.run_snyk_scan,
            self.check_security_headers,
            self.check_owasp_top10
        ]
        
        results = {}
        for test_func in tests:
            try:
                result = test_func()
                results[result["tool"]] = result
                print(f"✅ {result['tool']}: {'PASSED' if result['success'] else 'FAILED'}")
            except Exception as e:
                print(f"❌ {test_func.__name__}: ERROR - {str(e)}")
                results[test_func.__name__] = {
                    "tool": test_func.__name__,
                    "success": False,
                    "error": str(e)
                }
        
        # Generate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r.get("success", False))
        failed_tests = total_tests - passed_tests
        
        print("=" * 60)
        print(f"📊 Security Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Some security tests failed. Please review the results above.")
            return False
        else:
            print("\n✅ All security tests passed!")
            return True
    
    def save_results(self, filename: str = "security-test-results.json"):
        """Save test results to JSON file"""
        results_file = self.project_root / filename
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to {results_file}")

def main():
    """Main function"""
    tester = SecurityTester()
    
    # Check if required tools are installed
    required_tools = ["bandit", "safety", "semgrep", "snyk"]
    missing_tools = []
    
    for tool in required_tools:
        exit_code, _, _ = tester.run_command(["which", tool])
        if exit_code != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install them using:")
        print("  pip install bandit safety semgrep")
        print("  npm install -g @snyk/cli")
        sys.exit(1)
    
    # Run all tests
    success = tester.run_all_tests()
    tester.save_results()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
