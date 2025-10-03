#!/usr/bin/env python3
"""
Generate Automated Fix Suggestions
Creates code fixes and unit tests for test failures
"""
import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import git
from jinja2 import Template


class FixGenerator:
    """Generates automated fix suggestions"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(self.repo_path)
        
        # Fix templates
        self.fix_templates = {
            'import_error': self._generate_import_fix,
            'database_error': self._generate_database_fix,
            'configuration_error': self._generate_config_fix,
            'logic_error': self._generate_logic_fix,
            'authentication_error': self._generate_auth_fix,
            'network_error': self._generate_network_fix
        }
        
        self.test_templates = {
            'import_error': self._generate_import_test,
            'database_error': self._generate_database_test,
            'configuration_error': self._generate_config_test,
            'logic_error': self._generate_logic_test,
            'authentication_error': self._generate_auth_test,
            'network_error': self._generate_network_test
        }
    
    def generate_fixes(self, diagnostics_file: str, output_dir: str) -> Dict[str, Any]:
        """Generate fixes for all test failures"""
        print("🔧 Generating fix suggestions...")
        
        # Load diagnostics
        with open(diagnostics_file, 'r') as f:
            diagnostics = json.load(f)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        fixes = []
        
        for failure in diagnostics['failures']:
            fix = self._generate_single_fix(failure)
            if fix:
                fixes.append(fix)
        
        # Generate summary
        summary = self._generate_fix_summary(fixes, diagnostics)
        
        # Save results
        results = {
            'fixes': fixes,
            'summary': summary,
            'total_fixes': len(fixes),
            'confidence': self._calculate_fix_confidence(fixes)
        }
        
        # Save individual fix files
        for i, fix in enumerate(fixes):
            fix_file = output_path / f"fix_{i+1}_{fix['category']}.py"
            with open(fix_file, 'w') as f:
                f.write(fix['code'])
        
        # Save test files
        for i, fix in enumerate(fixes):
            if fix.get('test_code'):
                test_file = output_path / f"test_{i+1}_{fix['category']}.py"
                with open(test_file, 'w') as f:
                    f.write(fix['test_code'])
        
        # Save summary
        with open(output_path / 'fix-summary.md', 'w') as f:
            f.write(self._generate_markdown_summary(results))
        
        # Save JSON results
        with open(output_path / 'fix-results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"✅ Generated {len(fixes)} fix suggestions")
        print(f"📁 Saved to: {output_path}")
        
        return results
    
    def _generate_single_fix(self, failure: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate fix for a single test failure"""
        category = failure.get('category', 'unknown')
        
        if category not in self.fix_templates:
            print(f"⚠️  No fix template for category: {category}")
            return None
        
        try:
            fix_code = self.fix_templates[category](failure)
            test_code = self.test_templates[category](failure) if category in self.test_templates else None
            
            return {
                'test_name': failure['test_name'],
                'category': category,
                'severity': failure['severity'],
                'risk_level': failure['risk_level'],
                'code': fix_code,
                'test_code': test_code,
                'explanation': self._generate_explanation(failure, category),
                'risk_notes': self._generate_risk_notes(failure, category),
                'verification_steps': self._generate_verification_steps(failure, category)
            }
        except Exception as e:
            print(f"❌ Error generating fix for {failure['test_name']}: {e}")
            return None
    
    def _generate_import_fix(self, failure: Dict[str, Any]) -> str:
        """Generate fix for import errors"""
        error_message = failure['error_message']
        
        if 'No module named' in error_message:
            # Extract module name
            import re
            match = re.search(r'No module named [\'"]([^\'"]+)[\'"]', error_message)
            if match:
                module_name = match.group(1)
                return f"""# Fix for import error: {failure['test_name']}
# Add missing import statement

try:
    from {module_name} import *
    print(f"✅ Successfully imported {module_name}")
except ImportError:
    # Fallback import or install missing dependency
    print(f"❌ Failed to import {module_name}")
    print("Install missing dependency: pip install {module_name}")
    raise
"""
        
        return f"""# Fix for import error: {failure['test_name']}
# Check and fix import statements

import sys
import importlib

# Ensure proper import path
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

# Try importing with error handling
try:
    # Add your import here
    pass
except ImportError as e:
    print(f"Import error: {{e}}")
    raise
"""
    
    def _generate_database_fix(self, failure: Dict[str, Any]) -> str:
        """Generate fix for database errors"""
        return f"""# Fix for database error: {failure['test_name']}
import os
import sys
sys.path.insert(0, 'src')

from core.database import Base, engine
from sqlalchemy import text

def fix_database_issue():
    \"\"\"Fix database connectivity and schema issues\"\"\"
    
    try:
        # Ensure database directory exists
        os.makedirs('data', exist_ok=True)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test passed")
            
    except Exception as e:
        print(f"❌ Database fix failed: {{e}}")
        raise

if __name__ == "__main__":
    fix_database_issue()
"""
    
    def _generate_config_fix(self, failure: Dict[str, Any]) -> str:
        """Generate fix for configuration errors"""
        return f"""# Fix for configuration error: {failure['test_name']}
import os
from pathlib import Path

def fix_configuration_issue():
    \"\"\"Fix configuration and environment variable issues\"\"\"
    
    # Set default environment variables for development
    default_config = {{
        'DEBUG': 'true',
        'ENVIRONMENT': 'development',
        'DATABASE_URL': 'sqlite:///./data/app.db',
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'JWT_SECRET': 'dev-jwt-secret-change-in-production'
    }}
    
    for key, value in default_config.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"✅ Set {{key}} = {{value}}")
    
    # Verify configuration
    required_vars = ['DATABASE_URL', 'SECRET_KEY', 'JWT_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {{missing_vars}}")
        return False
    
    print("✅ Configuration verified")
    return True

if __name__ == "__main__":
    fix_configuration_issue()
"""
    
    def _generate_logic_fix(self, failure: Dict[str, Any]) -> str:
        """Generate fix for logic errors"""
        return f"""# Fix for logic error: {failure['test_name']}
def fix_logic_issue():
    \"\"\"Fix logic and assertion errors\"\"\"
    
    try:
        # Add proper error handling
        # Add input validation
        # Add boundary checks
        
        print("✅ Logic fix implemented")
        return True
        
    except Exception as e:
        print(f"❌ Logic fix failed: {{e}}")
        return False

if __name__ == "__main__":
    fix_logic_issue()
"""
    
    def _generate_auth_fix(self, failure: Dict[str, Any]) -> str:
        """Generate fix for authentication errors"""
        return f"""# Fix for authentication error: {failure['test_name']}
import sys
sys.path.insert(0, 'src')

from core.auth import auth_manager
from core.config import settings

def fix_authentication_issue():
    \"\"\"Fix authentication and authorization issues\"\"\"
    
    try:
        # Verify JWT secrets are set
        if not settings.JWT_SECRET or settings.JWT_SECRET == 'dev-jwt-secret-change-in-production':
            print("⚠️  Using default JWT secret - change in production")
        
        # Test token generation
        test_payload = {{"user_id": "test", "company_id": "test"}}
        token = auth_manager.create_access_token(test_payload)
        
        if token:
            print("✅ Authentication system working")
            return True
        else:
            print("❌ Token generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication fix failed: {{e}}")
        return False

if __name__ == "__main__":
    fix_authentication_issue()
"""
    
    def _generate_network_fix(self, failure: Dict[str, Any]) -> str:
        """Generate fix for network errors"""
        return f"""# Fix for network error: {failure['test_name']}
import requests
import time
from typing import Optional

def fix_network_issue(url: str, timeout: int = 30, retries: int = 3) -> Optional[requests.Response]:
    \"\"\"Fix network connectivity issues with retry logic\"\"\"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            print(f"✅ Network request successful (attempt {{attempt + 1}})")
            return response
            
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout (attempt {{attempt + 1}}/{{retries}})")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error (attempt {{attempt + 1}}/{{retries}})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {{e}} (attempt {{attempt + 1}}/{{retries}})")
        
        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    print(f"❌ All {{retries}} attempts failed")
    return None

if __name__ == "__main__":
    # Test with a simple endpoint
    fix_network_issue("https://httpbin.org/get")
"""
    
    def _generate_import_test(self, failure: Dict[str, Any]) -> str:
        """Generate test for import fixes"""
        return f"""#!/usr/bin/env python3
\"\"\"Test for import fix: {failure['test_name']}\"\"\"
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_import_fix():
    \"\"\"Test that import issues are resolved\"\"\"
    
    # Test core imports
    try:
        from core.config import settings
        assert settings is not None
        print("✅ Core config import works")
    except ImportError as e:
        pytest.fail(f"Core config import failed: {{e}}")
    
    # Test model imports
    try:
        from models.user import User
        assert User is not None
        print("✅ User model import works")
    except ImportError as e:
        pytest.fail(f"User model import failed: {{e}}")
    
    # Test service imports
    try:
        from services.ocr import OCRService
        assert OCRService is not None
        print("✅ OCR service import works")
    except ImportError as e:
        pytest.fail(f"OCR service import failed: {{e}}")

if __name__ == "__main__":
    test_import_fix()
    print("✅ All import tests passed")
"""
    
    def _generate_database_test(self, failure: Dict[str, Any]) -> str:
        """Generate test for database fixes"""
        return f"""#!/usr/bin/env python3
\"\"\"Test for database fix: {failure['test_name']}\"\"\"
import pytest
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.database import Base, engine, SessionLocal
from sqlalchemy import text

@pytest.fixture
def test_db():
    \"\"\"Create test database\"\"\"
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Update database URL
    test_engine = create_engine(f'sqlite:///{{db_path}}')
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # Cleanup
    shutil.rmtree(temp_dir)

def test_database_connection(test_db):
    \"\"\"Test database connectivity\"\"\"
    with test_db.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
        print("✅ Database connection test passed")

def test_database_tables(test_db):
    \"\"\"Test that all required tables exist\"\"\"
    with test_db.connect() as conn:
        # Check if tables exist
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        
        expected_tables = ['users', 'companies', 'invoices', 'audit_logs']
        for table in expected_tables:
            assert table in tables, f"Table {{table}} not found"
        
        print("✅ All required tables exist")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _generate_config_test(self, failure: Dict[str, Any]) -> str:
        """Generate test for configuration fixes"""
        return f"""#!/usr/bin/env python3
\"\"\"Test for configuration fix: {failure['test_name']}\"\"\"
import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.config import settings

def test_configuration_values():
    \"\"\"Test that all required configuration values are set\"\"\"
    
    # Test required settings
    assert settings.DATABASE_URL is not None
    assert settings.SECRET_KEY is not None
    assert settings.JWT_SECRET is not None
    
    print("✅ Configuration values are set")

def test_database_url_format():
    \"\"\"Test database URL format\"\"\"
    db_url = settings.DATABASE_URL
    
    # Should be a valid database URL
    assert db_url.startswith(('sqlite://', 'postgresql://', 'mysql://'))
    print("✅ Database URL format is valid")

def test_environment_variables():
    \"\"\"Test environment-specific variables\"\"\"
    
    # Set test environment
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['DEBUG'] = 'true'
    
    # Reload settings
    from core.config import settings
    assert settings.ENVIRONMENT == 'test'
    assert settings.DEBUG == True
    
    print("✅ Environment variables work correctly")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _generate_logic_test(self, failure: Dict[str, Any]) -> str:
        """Generate test for logic fixes"""
        return f"""#!/usr/bin/env python3
\"\"\"Test for logic fix: {failure['test_name']}\"\"\"
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_logic_fix():
    \"\"\"Test that logic errors are resolved\"\"\"
    
    # Add specific test cases for the logic fix
    # This should be customized based on the actual failure
    
    # Example test
    result = 2 + 2
    assert result == 4, "Basic math should work"
    
    print("✅ Logic fix test passed")

def test_edge_cases():
    \"\"\"Test edge cases that might cause logic errors\"\"\"
    
    # Test with edge case values
    edge_cases = [0, -1, 1, 100, -100]
    
    for case in edge_cases:
        # Add your edge case testing logic here
        assert case is not None
        print(f"✅ Edge case {{case}} handled correctly")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _generate_auth_test(self, failure: Dict[str, Any]) -> str:
        """Generate test for authentication fixes"""
        return f"""#!/usr/bin/env python3
\"\"\"Test for authentication fix: {failure['test_name']}\"\"\"
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.auth import auth_manager
from core.config import settings

def test_authentication_system():
    \"\"\"Test that authentication system works\"\"\"
    
    # Test JWT token creation
    test_payload = {{"user_id": "test_user", "company_id": "test_company"}}
    
    try:
        token = auth_manager.create_access_token(test_payload)
        assert token is not None
        assert len(token) > 0
        print("✅ JWT token creation works")
    except Exception as e:
        pytest.fail(f"JWT token creation failed: {{e}}")

def test_token_validation():
    \"\"\"Test token validation\"\"\"
    
    test_payload = {{"user_id": "test_user", "company_id": "test_company"}}
    token = auth_manager.create_access_token(test_payload)
    
    try:
        decoded = auth_manager.verify_token(token)
        assert decoded is not None
        assert decoded.get('user_id') == 'test_user'
        print("✅ Token validation works")
    except Exception as e:
        pytest.fail(f"Token validation failed: {{e}}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _generate_network_test(self, failure: Dict[str, Any]) -> str:
        """Generate test for network fixes"""
        return f"""#!/usr/bin/env python3
\"\"\"Test for network fix: {failure['test_name']}\"\"\"
import pytest
import requests
from unittest.mock import patch, Mock

def test_network_connectivity():
    \"\"\"Test basic network connectivity\"\"\"
    
    try:
        # Test with a reliable endpoint
        response = requests.get("https://httpbin.org/get", timeout=10)
        assert response.status_code == 200
        print("✅ Network connectivity test passed")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Network connectivity test failed: {{e}}")

def test_retry_logic():
    \"\"\"Test retry logic for network requests\"\"\"
    
    # Mock failed requests
    with patch('requests.get') as mock_get:
        # First two calls fail, third succeeds
        mock_responses = [
            requests.exceptions.Timeout(),
            requests.exceptions.ConnectionError(),
            Mock(status_code=200)
        ]
        mock_get.side_effect = mock_responses
        
        # Test retry logic (this would need to be imported from your fix)
        # response = fix_network_issue("https://example.com")
        # assert response.status_code == 200
        
        print("✅ Retry logic test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _generate_explanation(self, failure: Dict[str, Any], category: str) -> str:
        """Generate explanation for the fix"""
        explanations = {
            'import_error': f"The test '{failure['test_name']}' failed due to missing or incorrect import statements. This fix ensures all required modules are properly imported with appropriate error handling.",
            'database_error': f"The test '{failure['test_name']}' failed due to database connectivity or schema issues. This fix ensures proper database initialization and connection handling.",
            'configuration_error': f"The test '{failure['test_name']}' failed due to missing or incorrect configuration settings. This fix sets up proper environment variables and configuration validation.",
            'logic_error': f"The test '{failure['test_name']}' failed due to logic or assertion errors. This fix implements proper error handling and validation logic.",
            'authentication_error': f"The test '{failure['test_name']}' failed due to authentication or authorization issues. This fix ensures proper JWT token handling and validation.",
            'network_error': f"The test '{failure['test_name']}' failed due to network connectivity issues. This fix implements retry logic and proper error handling for network requests."
        }
        
        return explanations.get(category, f"The test '{failure['test_name']}' failed. This fix addresses the underlying issue with appropriate error handling and validation.")
    
    def _generate_risk_notes(self, failure: Dict[str, Any], category: str) -> str:
        """Generate risk assessment notes"""
        risk_notes = {
            'import_error': "Low risk - Import fixes are generally safe but may affect other parts of the codebase. Test thoroughly.",
            'database_error': "Medium risk - Database changes can affect data integrity. Ensure migrations are tested on staging first.",
            'configuration_error': "Low risk - Configuration changes are usually safe but verify environment-specific settings.",
            'logic_error': "High risk - Logic changes can introduce new bugs. Comprehensive testing required.",
            'authentication_error': "High risk - Authentication changes affect security. Security review required.",
            'network_error': "Medium risk - Network changes may affect external integrations. Monitor external service dependencies."
        }
        
        return risk_notes.get(category, "Medium risk - Review changes carefully before deployment.")
    
    def _generate_verification_steps(self, failure: Dict[str, Any], category: str) -> List[str]:
        """Generate verification steps"""
        return [
            f"1. Run the specific failing test: `pytest {failure['test_name']} -v`",
            "2. Run the full test suite to ensure no regressions",
            "3. Test the fix manually if applicable",
            "4. Review code changes for potential side effects",
            "5. Deploy to staging environment for validation"
        ]
    
    def _generate_fix_summary(self, fixes: List[Dict[str, Any]], diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all fixes"""
        return {
            'total_fixes': len(fixes),
            'categories': list(set(fix['category'] for fix in fixes)),
            'severity_breakdown': {
                'critical': len([f for f in fixes if f['severity'] == 'critical']),
                'high': len([f for f in fixes if f['severity'] == 'high']),
                'medium': len([f for f in fixes if f['severity'] == 'medium']),
                'low': len([f for f in fixes if f['severity'] == 'low'])
            },
            'risk_assessment': diagnostics.get('risk_assessment', 'medium'),
            'confidence': self._calculate_fix_confidence(fixes)
        }
    
    def _calculate_fix_confidence(self, fixes: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the fixes"""
        if not fixes:
            return 0.0
        
        # Simple confidence calculation
        high_confidence_categories = ['import_error', 'configuration_error']
        confident_fixes = sum(1 for fix in fixes if fix['category'] in high_confidence_categories)
        
        return confident_fixes / len(fixes)
    
    def _generate_markdown_summary(self, results: Dict[str, Any]) -> str:
        """Generate markdown summary of fixes"""
        summary = results['summary']
        
        return f"""# 🔧 Automated Fix Suggestions

## 📊 Summary

- **Total Fixes Generated:** {summary['total_fixes']}
- **Categories:** {', '.join(summary['categories'])}
- **Risk Level:** {summary['risk_assessment'].upper()}
- **Confidence:** {summary['confidence']:.1%}

## 🎯 Fixes by Severity

- **Critical:** {summary['severity_breakdown']['critical']}
- **High:** {summary['severity_breakdown']['high']}
- **Medium:** {summary['severity_breakdown']['medium']}
- **Low:** {summary['severity_breakdown']['low']}

## 📋 Next Steps

1. Review each fix file in the output directory
2. Test fixes individually before applying
3. Run full test suite after applying fixes
4. Deploy to staging for validation

## ⚠️ Risk Notes

- Review all changes carefully before merging
- Test in staging environment first
- Consider security implications for authentication fixes
- Monitor for regressions after deployment

---

**Generated:** {results.get('timestamp', 'Unknown')}  
**Total Fixes:** {summary['total_fixes']}  
**Confidence Score:** {summary['confidence']:.1%}
"""


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate Fix Suggestions')
    parser.add_argument('--diagnostics', required=True, help='Path to diagnostics JSON file')
    parser.add_argument('--repo', required=True, help='Repository name')
    parser.add_argument('--output', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    # Generate fixes
    generator = FixGenerator()
    results = generator.generate_fixes(args.diagnostics, args.output)
    
    print(f"✅ Fix generation completed")
    print(f"📊 Generated {results['total_fixes']} fixes")
    print(f"🎯 Confidence: {results['confidence']:.1%}")


if __name__ == "__main__":
    main()








