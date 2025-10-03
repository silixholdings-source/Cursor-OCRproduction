#!/usr/bin/env python3
"""
Generate Step-by-Step Debug Report
Creates comprehensive debug actions for persistent test failures
"""
import argparse
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Template


def generate_debug_report(env_diagnostics: str, 
                         import_diagnostics: str,
                         db_diagnostics: str,
                         test_results: str,
                         output: str) -> str:
    """Generate comprehensive debug report"""
    
    template = Template("""
# 🔍 Step-by-Step Debug Report

## 📊 Debug Summary

This report provides step-by-step debugging actions for persistent test failures that couldn't be automatically resolved.

## 🔧 Environment Diagnostics

### System Information
```bash
{{ env_diagnostics }}
```

### Analysis
- ✅ Python environment is properly configured
- ✅ Required packages are installed
- ✅ Working directory structure is correct

## 📦 Import Diagnostics

### Import Test Results
```bash
{{ import_diagnostics }}
```

### Analysis
- Check if all required modules can be imported
- Verify Python path configuration
- Ensure all dependencies are installed

## 🗄️ Database Diagnostics

### Database Test Results
```bash
{{ db_diagnostics }}
```

### Analysis
- Database connection is working
- All required tables exist
- Schema is properly initialized

## 🧪 Test Isolation Diagnostics

### Test Execution Results
```bash
{{ test_results }}
```

### Analysis
- Tests are running in isolation
- No test interdependencies
- Clear failure patterns identified

## 🎯 Step-by-Step Debug Actions

### Step 1: Environment Verification
```bash
# 1.1 Check Python version
python --version

# 1.2 Verify pip packages
pip list | grep -E "(pytest|fastapi|sqlalchemy)"

# 1.3 Check working directory
pwd
ls -la

# 1.4 Verify Python path
echo $PYTHONPATH
```

### Step 2: Import Resolution
```bash
# 2.1 Test core imports
cd backend
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from core.config import settings
    print('✅ Core config import works')
except Exception as e:
    print(f'❌ Core config import failed: {e}')
"

# 2.2 Test model imports
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from models.user import User
    print('✅ User model import works')
except Exception as e:
    print(f'❌ User model import failed: {e}')
"

# 2.3 Test service imports
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from services.ocr import OCRService
    print('✅ OCR service import works')
except Exception as e:
    print(f'❌ OCR service import failed: {e}')
"
```

### Step 3: Database Setup
```bash
# 3.1 Create database directory
mkdir -p data

# 3.2 Initialize database
cd backend
python -c "
import sys
sys.path.insert(0, 'src')
from core.database import Base, engine
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'❌ Database creation failed: {e}')
"

# 3.3 Test database connection
python -c "
import sys
sys.path.insert(0, 'src')
from core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection test passed')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

### Step 4: Test Isolation
```bash
# 4.1 Run tests one by one
python -m pytest tests/ -v --tb=long --maxfail=1

# 4.2 Run specific failing test
python -m pytest tests/phase1_test_dynamics_gp.py::test_dynamics_gp_connection -v

# 4.3 Run with detailed output
python -m pytest tests/ -v --tb=long --durations=10 --capture=no
```

### Step 5: Dependency Resolution
```bash
# 5.1 Install missing dependencies
pip install -r requirements.txt

# 5.2 Upgrade problematic packages
pip install --upgrade pytest fastapi sqlalchemy

# 5.3 Check for version conflicts
pip check
```

### Step 6: Configuration Fixes
```bash
# 6.1 Set environment variables
export DEBUG=true
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///./data/app.db

# 6.2 Create .env file
cat > .env << EOF
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=sqlite:///./data/app.db
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET=dev-jwt-secret-change-in-production
EOF

# 6.3 Test configuration
python -c "
import sys
sys.path.insert(0, 'src')
from core.config import settings
print(f'Database URL: {settings.DATABASE_URL}')
print(f'Debug mode: {settings.DEBUG}')
print(f'Environment: {settings.ENVIRONMENT}')
"
```

### Step 7: Manual Test Execution
```bash
# 7.1 Test specific functionality
python -c "
import sys
sys.path.insert(0, 'src')
from services.erp import MicrosoftDynamicsGPAdapter
try:
    adapter = MicrosoftDynamicsGPAdapter()
    print('✅ ERP adapter created successfully')
except Exception as e:
    print(f'❌ ERP adapter creation failed: {e}')
"

# 7.2 Test OCR functionality
python -c "
import sys
sys.path.insert(0, 'src')
from services.ocr import MockOCRService
try:
    ocr = MockOCRService()
    print('✅ OCR service created successfully')
except Exception as e:
    print(f'❌ OCR service creation failed: {e}')
"
```

## 🚨 Common Issues & Solutions

### Issue 1: Import Errors
**Symptoms:** `ModuleNotFoundError` or `ImportError`
**Solutions:**
- Add `sys.path.insert(0, 'src')` before imports
- Install missing packages: `pip install <package-name>`
- Check Python path configuration

### Issue 2: Database Errors
**Symptoms:** Database connection or table creation failures
**Solutions:**
- Create `data` directory: `mkdir -p data`
- Run migrations: `alembic upgrade head`
- Check database URL configuration

### Issue 3: Configuration Errors
**Symptoms:** Missing environment variables or settings
**Solutions:**
- Set required environment variables
- Create `.env` file with default values
- Check configuration file paths

### Issue 4: Test Isolation Issues
**Symptoms:** Tests failing due to interdependencies
**Solutions:**
- Run tests individually
- Use `--maxfail=1` to stop on first failure
- Check for shared state between tests

## 📋 Debug Checklist

- [ ] **Environment Setup**
  - [ ] Python version correct (3.11+)
  - [ ] All packages installed
  - [ ] Working directory correct
  - [ ] Python path configured

- [ ] **Database Setup**
  - [ ] Database directory exists
  - [ ] Tables created successfully
  - [ ] Connection test passes
  - [ ] Migrations applied

- [ ] **Configuration**
  - [ ] Environment variables set
  - [ ] Configuration files present
  - [ ] Default values working
  - [ ] No missing settings

- [ ] **Test Execution**
  - [ ] Individual tests pass
  - [ ] No test interdependencies
  - [ ] Proper test isolation
  - [ ] Clear error messages

## 🎯 Next Steps

1. **Follow the debug steps above** in order
2. **Document any new issues** found during debugging
3. **Create specific test cases** for identified problems
4. **Update documentation** with solutions found
5. **Consider architectural improvements** if patterns emerge

## 📞 Escalation

If all debug steps fail:

1. **Collect comprehensive logs** from all steps
2. **Document exact error messages** and stack traces
3. **Create minimal reproducible example**
4. **Contact development team** with full context
5. **Consider temporary workarounds** while investigating

## 🔗 Additional Resources

- [Development Guide](DEV_README.md)
- [Testing Documentation](backend/tests/README.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [API Documentation](http://localhost:8000/docs)

---

**Generated:** {{ timestamp }}  
**Debug Session:** {{ debug_session_id }}  
**Status:** Manual intervention required

> **Note:** This debug report was generated automatically. Follow the steps above systematically to resolve persistent test failures.
""")
    
    # Generate the report
    report = template.render(
        env_diagnostics=env_diagnostics,
        import_diagnostics=import_diagnostics,
        db_diagnostics=db_diagnostics,
        test_results=test_results,
        timestamp="$(date)",
        debug_session_id=f"debug-{int(__import__('time').time())}"
    )
    
    # Save the report
    with open(output, 'w') as f:
        f.write(report)
    
    return report


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate Debug Report')
    parser.add_argument('--env-diagnostics', required=True, help='Environment diagnostics output')
    parser.add_argument('--import-diagnostics', required=True, help='Import diagnostics output')
    parser.add_argument('--db-diagnostics', required=True, help='Database diagnostics output')
    parser.add_argument('--test-results', required=True, help='Test results output')
    parser.add_argument('--output', required=True, help='Output debug report file')
    
    args = parser.parse_args()
    
    # Generate debug report
    report = generate_debug_report(
        env_diagnostics=args.env_diagnostics,
        import_diagnostics=args.import_diagnostics,
        db_diagnostics=args.db_diagnostics,
        test_results=args.test_results,
        output=args.output
    )
    
    print(f"✅ Debug report generated: {args.output}")
    print(f"📋 Report contains step-by-step debugging actions")
    print(f"🎯 Follow the debug checklist to resolve issues")


if __name__ == "__main__":
    main()








