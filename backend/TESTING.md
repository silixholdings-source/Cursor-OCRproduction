# Testing Guide for AI ERP SaaS Backend

This document provides comprehensive information about testing the FastAPI backend application.

## 🧪 Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── utils.py             # Test utilities and helpers
│   ├── test_auth.py         # Authentication tests
│   ├── test_file_upload.py  # File upload tests
│   ├── test_invoice_extraction.py  # Invoice extraction tests
│   ├── test_invoice_retrieval.py   # Invoice retrieval tests
│   ├── test_integration.py  # Integration tests
│   └── test_performance.py  # Performance tests
├── pytest.ini              # Pytest configuration
├── requirements-dev.txt     # Development dependencies
├── run_tests.py            # Test runner script
└── Makefile               # Development commands
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for integration tests)
- Redis (for integration tests)

### Installation
```bash
# Install dependencies
make install

# Or manually
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

#### All Tests
```bash
make test
# or
python run_tests.py --all --coverage
```

#### Specific Test Types
```bash
# Unit tests only
make test-unit
python run_tests.py --unit

# Integration tests only
make test-integration
python run_tests.py --integration

# Performance tests only
make test-performance
python run_tests.py --performance
```

#### With Coverage
```bash
make test-coverage
python run_tests.py --all --coverage --html
```

## 📋 Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual functions and methods in isolation
- **Scope**: Single functions, classes, or modules
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast (< 1 second per test)

**Examples**:
- Authentication logic
- Data validation
- Business logic functions
- Utility functions

### 2. Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test interaction between different components
- **Scope**: Multiple modules working together
- **Dependencies**: Real database, external services
- **Speed**: Medium (1-10 seconds per test)

**Examples**:
- API endpoints with database
- File upload with OCR processing
- Complete invoice workflow
- Authentication flow

### 3. Performance Tests (`@pytest.mark.performance`)
- **Purpose**: Test system performance under load
- **Scope**: End-to-end system performance
- **Dependencies**: Full system with large datasets
- **Speed**: Slow (10+ seconds per test)

**Examples**:
- Large dataset queries
- Concurrent request handling
- Memory usage
- Response time benchmarks

## 🔧 Test Configuration

### Environment Variables
```bash
export DATABASE_URL="postgresql://user:pass@localhost/test_db"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="test_secret_key"
export ENVIRONMENT="testing"
export OCR_SERVICE_URL="http://localhost:8001"
```

### Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    auth: Authentication related tests
    ocr: OCR related tests
    invoice: Invoice related tests
    file_upload: File upload tests
```

## 🛠️ Test Fixtures

### Database Fixtures
```python
@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    
@pytest.fixture
def test_company(db_session):
    """Create a test company."""
    
@pytest.fixture
def test_user(db_session, test_company):
    """Create a test user."""
```

### Authentication Fixtures
```python
@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
```

### Data Fixtures
```python
@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    
@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    
@pytest.fixture
def mock_ocr_response():
    """Mock OCR response data."""
```

## 📝 Writing Tests

### Test File Structure
```python
"""
Tests for [module/feature] functionality
"""
import pytest
from fastapi.testclient import TestClient

@pytest.mark.unit  # or @pytest.mark.integration
class TestFeatureName:
    """Test [feature] functionality."""

    def test_specific_functionality(self, client: TestClient, auth_headers: dict):
        """Test specific functionality."""
        # Arrange
        test_data = {"key": "value"}
        
        # Act
        response = client.post("/api/endpoint", json=test_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == "value"
```

### Test Naming Convention
- **Test files**: `test_*.py`
- **Test classes**: `Test*`
- **Test methods**: `test_*`
- **Descriptive names**: `test_user_login_with_valid_credentials`

### Assertion Patterns
```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201
assert response.status_code == 400

# Response data
assert "key" in response.json()
assert response.json()["key"] == expected_value
assert len(response.json()["items"]) == expected_count

# Database state
assert db_session.query(Model).count() == expected_count
assert db_session.query(Model).filter_by(id=id).first() is not None
```

## 🐳 Docker Testing

### Test with Docker Compose
```bash
# Run all tests in Docker
make docker-test

# Or manually
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

### Test Services
- **PostgreSQL**: Test database on port 5433
- **Redis**: Test cache on port 6380
- **OCR Service**: Mock OCR service on port 8002
- **Backend**: Test API on port 8001

## 📊 Coverage Reports

### Generate Coverage
```bash
# Terminal coverage
make test-coverage

# HTML coverage report
make test-coverage
open htmlcov/index.html

# XML coverage (for CI)
python run_tests.py --all --coverage
```

### Coverage Targets
- **Overall**: 80% minimum
- **Critical paths**: 90% minimum
- **New code**: 90% minimum

## 🔍 Debugging Tests

### Verbose Output
```bash
python run_tests.py --unit --verbose
pytest tests/ -v -s
```

### Run Specific Test
```bash
pytest tests/test_auth.py::TestAuthentication::test_user_login_success -v
```

### Debug Mode
```bash
pytest tests/ --pdb
```

### Test Discovery
```bash
pytest --collect-only
```

## 🚀 CI/CD Integration

### GitHub Actions
The project includes a comprehensive CI/CD pipeline (`.github/workflows/ci.yml`) that:

1. **Runs on**: Push to main/develop, Pull requests
2. **Tests**: Backend, Frontend, OCR service
3. **Checks**: Linting, Type checking, Security scanning
4. **Deploys**: Staging (develop), Production (main)

### Local CI Simulation
```bash
make ci
```

## 📈 Performance Testing

### Load Testing
```bash
# Run performance tests
make test-performance

# With specific load
python run_tests.py --performance --parallel 4
```

### Benchmarking
```bash
pytest tests/test_performance.py --benchmark-only
```

## 🛡️ Security Testing

### Security Checks
```bash
make security
bandit -r src -f json -o bandit-report.json
```

### Vulnerability Scanning
```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check
```

## 📚 Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Keep tests independent
- Clean up after tests

### 2. Test Data
- Use factories for test data
- Create minimal test data
- Use realistic test data
- Clean up test data

### 3. Assertions
- One assertion per test (when possible)
- Use specific assertions
- Test both success and failure cases
- Test edge cases

### 4. Mocking
- Mock external dependencies
- Mock slow operations
- Mock network calls
- Use realistic mock data

### 5. Performance
- Keep unit tests fast
- Use appropriate test markers
- Run slow tests separately
- Monitor test execution time

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection string
echo $DATABASE_URL
```

#### Import Errors
```bash
# Install dependencies
make install

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Test Failures
```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific test
pytest tests/test_auth.py::TestAuthentication::test_user_login_success -v
```

#### Coverage Issues
```bash
# Check coverage configuration
cat pytest.ini

# Generate detailed coverage
pytest tests/ --cov=src --cov-report=html
```

## 📞 Support

For testing questions or issues:
1. Check this documentation
2. Review test examples in the codebase
3. Check GitHub Issues
4. Contact the development team

## 🔄 Continuous Improvement

### Regular Tasks
- Review test coverage monthly
- Update test data quarterly
- Refactor slow tests
- Add tests for new features

### Metrics to Track
- Test execution time
- Coverage percentage
- Flaky test frequency
- Test maintenance effort









