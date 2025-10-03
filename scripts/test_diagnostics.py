#!/usr/bin/env python3
"""
Intelligent Test Diagnostics System
Analyzes test failures and provides detailed diagnostics
"""
import json
import os
import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import git
import requests


@dataclass
class TestFailure:
    """Represents a single test failure"""
    test_name: str
    file_path: str
    line_number: int
    error_type: str
    error_message: str
    stack_trace: str
    severity: str  # critical, high, medium, low
    category: str  # import, database, logic, configuration, etc.
    suggested_fix: Optional[str] = None
    risk_level: str = "medium"


@dataclass
class DiagnosticResult:
    """Complete diagnostic analysis"""
    commit_sha: str
    branch: str
    repository: str
    timestamp: datetime
    total_tests: int
    failed_tests: int
    passed_tests: int
    failures: List[TestFailure]
    root_causes: List[str]
    suggested_actions: List[str]
    risk_assessment: str
    confidence_score: float


class TestDiagnostics:
    """Intelligent test failure diagnostics"""
    
    def __init__(self, test_results_dir: str, commit_sha: str, repo: str, branch: str):
        self.test_results_dir = Path(test_results_dir)
        self.commit_sha = commit_sha
        self.repo = repo
        self.branch = branch
        self.failures: List[TestFailure] = []
        self.root_causes: List[str] = []
        
        # Error pattern matching
        self.error_patterns = {
            'import_error': [
                r'ModuleNotFoundError: No module named',
                r'ImportError:',
                r'cannot import name',
                r'No module named'
            ],
            'database_error': [
                r'database.*error',
                r'connection.*failed',
                r'table.*does not exist',
                r'column.*does not exist',
                r'SQLAlchemy.*Error',
                r'psycopg2.*Error'
            ],
            'configuration_error': [
                r'configuration.*error',
                r'environment.*variable',
                r'setting.*not found',
                r'config.*missing'
            ],
            'authentication_error': [
                r'authentication.*failed',
                r'unauthorized',
                r'token.*invalid',
                r'permission.*denied'
            ],
            'network_error': [
                r'connection.*refused',
                r'timeout',
                r'network.*error',
                r'HTTP.*error'
            ],
            'logic_error': [
                r'AssertionError',
                r'ValueError',
                r'TypeError',
                r'KeyError',
                r'AttributeError'
            ]
        }
    
    def analyze_test_results(self) -> DiagnosticResult:
        """Analyze test results and generate diagnostics"""
        print("🔍 Analyzing test results...")
        
        # Parse test result files
        self._parse_junit_xml()
        self._parse_pytest_output()
        self._analyze_coverage_reports()
        
        # Analyze failures
        self._categorize_failures()
        self._identify_root_causes()
        self._generate_suggestions()
        
        # Generate final result
        result = DiagnosticResult(
            commit_sha=self.commit_sha,
            branch=self.branch,
            repository=self.repo,
            timestamp=datetime.now(),
            total_tests=self._count_total_tests(),
            failed_tests=len(self.failures),
            passed_tests=self._count_total_tests() - len(self.failures),
            failures=self.failures,
            root_causes=self.root_causes,
            suggested_actions=self._generate_suggested_actions(),
            risk_assessment=self._assess_risk(),
            confidence_score=self._calculate_confidence()
        )
        
        return result
    
    def _parse_junit_xml(self):
        """Parse JUnit XML test results"""
        junit_file = self.test_results_dir / "backend" / "test-results.xml"
        if not junit_file.exists():
            print(f"⚠️  JUnit XML not found: {junit_file}")
            return
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(junit_file)
            root = tree.getroot()
            
            for testcase in root.findall('.//testcase'):
                failure = testcase.find('failure')
                if failure is not None:
                    test_name = f"{testcase.get('classname')}.{testcase.get('name')}"
                    file_path = testcase.get('file', '')
                    line_number = int(testcase.get('line', 0))
                    
                    failure_obj = TestFailure(
                        test_name=test_name,
                        file_path=file_path,
                        line_number=line_number,
                        error_type=failure.get('type', 'Unknown'),
                        error_message=failure.text or '',
                        stack_trace=failure.text or '',
                        severity='medium',
                        category='unknown'
                    )
                    self.failures.append(failure_obj)
        
        except Exception as e:
            print(f"❌ Error parsing JUnit XML: {e}")
    
    def _parse_pytest_output(self):
        """Parse pytest output files"""
        pytest_files = list(self.test_results_dir.glob("**/pytest-output*.txt"))
        
        for pytest_file in pytest_files:
            try:
                with open(pytest_file, 'r') as f:
                    content = f.read()
                    self._extract_failures_from_pytest_output(content)
            except Exception as e:
                print(f"❌ Error parsing pytest output: {e}")
    
    def _extract_failures_from_pytest_output(self, content: str):
        """Extract failure information from pytest output"""
        # Simple regex patterns to extract test failures
        failure_pattern = r'FAILED\s+([^\s]+)::([^\s]+)\s+-\s+(.+)'
        error_pattern = r'ERROR\s+([^\s]+)::([^\s]+)\s+-\s+(.+)'
        
        for match in re.finditer(failure_pattern, content):
            class_name = match.group(1)
            test_name = match.group(2)
            error_msg = match.group(3)
            
            failure_obj = TestFailure(
                test_name=f"{class_name}.{test_name}",
                file_path=class_name.replace('.', '/') + '.py',
                line_number=0,
                error_type='FAILED',
                error_message=error_msg,
                stack_trace=error_msg,
                severity='high',
                category='unknown'
            )
            self.failures.append(failure_obj)
    
    def _analyze_coverage_reports(self):
        """Analyze test coverage reports"""
        coverage_file = self.test_results_dir / "backend" / "coverage.xml"
        if coverage_file.exists():
            print("📊 Analyzing coverage report...")
            # Add coverage analysis logic here
    
    def _categorize_failures(self):
        """Categorize failures by type and severity"""
        for failure in self.failures:
            failure.category = self._classify_error(failure.error_message)
            failure.severity = self._assess_severity(failure)
            failure.suggested_fix = self._suggest_fix(failure)
            failure.risk_level = self._assess_risk_level(failure)
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type based on message patterns"""
        error_lower = error_message.lower()
        
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_lower):
                    return category
        
        return 'unknown'
    
    def _assess_severity(self, failure: TestFailure) -> str:
        """Assess severity of test failure"""
        if failure.category == 'import_error':
            return 'critical'
        elif failure.category == 'database_error':
            return 'high'
        elif failure.category == 'configuration_error':
            return 'high'
        elif failure.category == 'authentication_error':
            return 'high'
        elif failure.category == 'network_error':
            return 'medium'
        else:
            return 'low'
    
    def _suggest_fix(self, failure: TestFailure) -> str:
        """Generate suggested fix for test failure"""
        if failure.category == 'import_error':
            return self._suggest_import_fix(failure)
        elif failure.category == 'database_error':
            return self._suggest_database_fix(failure)
        elif failure.category == 'configuration_error':
            return self._suggest_config_fix(failure)
        else:
            return "Review error message and implement appropriate fix"
    
    def _suggest_import_fix(self, failure: TestFailure) -> str:
        """Suggest fix for import errors"""
        error_msg = failure.error_message
        
        if 'No module named' in error_msg:
            module_name = re.search(r'No module named [\'"]([^\'"]+)[\'"]', error_msg)
            if module_name:
                return f"Add missing import: `from {module_name.group(1)} import ...`"
        
        if 'cannot import name' in error_msg:
            return "Check import statement and ensure the imported name exists"
        
        return "Fix import statement or install missing dependency"
    
    def _suggest_database_fix(self, failure: TestFailure) -> str:
        """Suggest fix for database errors"""
        error_msg = failure.error_message.lower()
        
        if 'table' in error_msg and 'does not exist' in error_msg:
            return "Run database migrations: `alembic upgrade head`"
        
        if 'column' in error_msg and 'does not exist' in error_msg:
            return "Update database schema or create new migration"
        
        if 'connection' in error_msg:
            return "Check database connection settings and ensure database is running"
        
        return "Review database configuration and schema"
    
    def _suggest_config_fix(self, failure: TestFailure) -> str:
        """Suggest fix for configuration errors"""
        return "Check environment variables and configuration files"
    
    def _assess_risk_level(self, failure: TestFailure) -> str:
        """Assess risk level of test failure"""
        if failure.severity == 'critical':
            return 'high'
        elif failure.severity == 'high':
            return 'medium'
        else:
            return 'low'
    
    def _identify_root_causes(self):
        """Identify root causes of test failures"""
        if not self.failures:
            return
        
        # Group failures by category
        categories = {}
        for failure in self.failures:
            if failure.category not in categories:
                categories[failure.category] = []
            categories[failure.category].append(failure)
        
        # Identify most common issues
        for category, failures in categories.items():
            if len(failures) > 1:
                self.root_causes.append(f"Multiple {category} failures ({len(failures)} tests)")
            else:
                self.root_causes.append(f"Single {category} failure")
    
    def _generate_suggestions(self):
        """Generate actionable suggestions"""
        # This will be populated by the analysis
        pass
    
    def _generate_suggested_actions(self) -> List[str]:
        """Generate list of suggested actions"""
        actions = []
        
        if any(f.category == 'import_error' for f in self.failures):
            actions.append("Fix import statements and ensure all dependencies are installed")
        
        if any(f.category == 'database_error' for f in self.failures):
            actions.append("Run database migrations and verify database connectivity")
        
        if any(f.category == 'configuration_error' for f in self.failures):
            actions.append("Check environment variables and configuration files")
        
        actions.append("Review and fix failing test cases")
        actions.append("Run tests locally before pushing changes")
        
        return actions
    
    def _assess_risk(self) -> str:
        """Assess overall risk level"""
        critical_count = sum(1 for f in self.failures if f.severity == 'critical')
        high_count = sum(1 for f in self.failures if f.severity == 'high')
        
        if critical_count > 0:
            return 'high'
        elif high_count > 2:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score for diagnostics"""
        if not self.failures:
            return 1.0
        
        # Simple confidence calculation based on error categorization
        categorized = sum(1 for f in self.failures if f.category != 'unknown')
        return categorized / len(self.failures)
    
    def _count_total_tests(self) -> int:
        """Count total number of tests"""
        # This would be extracted from test results
        return len(self.failures) + 10  # Placeholder


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Diagnostics')
    parser.add_argument('--test-results', required=True, help='Path to test results directory')
    parser.add_argument('--commit-sha', required=True, help='Commit SHA')
    parser.add_argument('--repo', required=True, help='Repository name')
    parser.add_argument('--branch', required=True, help='Branch name')
    parser.add_argument('--output', required=True, help='Output JSON file')
    
    args = parser.parse_args()
    
    # Run diagnostics
    diagnostics = TestDiagnostics(
        test_results_dir=args.test_results,
        commit_sha=args.commit_sha,
        repo=args.repo,
        branch=args.branch
    )
    
    result = diagnostics.analyze_test_results()
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(asdict(result), f, indent=2, default=str)
    
    print(f"✅ Diagnostics completed. Results saved to {args.output}")
    print(f"📊 Found {len(result.failures)} test failures")
    print(f"🎯 Risk level: {result.risk_assessment}")
    print(f"📈 Confidence: {result.confidence_score:.2f}")


if __name__ == "__main__":
    main()








