# AI ERP SaaS Development Environment

This document provides comprehensive instructions for setting up and using the AI ERP SaaS development environment.

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Git** for version control
- **PowerShell** (Windows) or **Bash** (Linux/Mac)

### One-Command Setup
```bash
# Run the automated setup script
python setup_dev.py
```

This will:
1. ✅ Check Docker availability
2. 🔨 Build all Docker images
3. 🗄️ Start PostgreSQL and Redis
4. 📋 Run database migrations
5. 🌱 Seed test data
6. 🏥 Verify all services are healthy
7. 🚀 Start the application
8. 🧪 Run initial smoke tests

## 🛠️ Development Commands

### Using Makefile (Recommended)
```bash
# Show all available commands
make help

# Start development environment
make start

# Stop all services
make stop

# Restart services
make restart

# View logs
make logs

# Run all tests
make test

# Run specific test phases
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-ocr          # OCR regression tests
make test-erp          # ERP integration tests

# Code quality
make lint              # Run linting checks
make format            # Format code automatically
make type-check        # Run type checking

# Database operations
make migrate           # Run migrations
make seed             # Seed test data
make db-reset         # Reset development database

# Utilities
make status            # Check service status
make health            # Run health checks
make clean             # Clean up containers
```

### Using Docker Compose Directly
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Start specific services
docker-compose -f docker-compose.dev.yml up -d postgres redis

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild images
docker-compose -f docker-compose.dev.yml build --no-cache
```

## 🏗️ Architecture Overview

### Services
- **Backend API** (FastAPI) - Port 8000
- **Web Frontend** (Next.js) - Port 3000
- **PostgreSQL** - Port 5432
- **Redis** - Port 6379
- **Celery Worker** - Background processing
- **Test Runner** - Isolated testing environment

### Development Features
- 🔄 **Hot Reload** - Backend and frontend auto-restart on code changes
- 🧪 **Isolated Testing** - Separate test database and services
- 📊 **Coverage Reports** - HTML and terminal coverage output
- 🔍 **Health Checks** - Automatic service health monitoring
- 📝 **Comprehensive Logging** - Structured logging for all services

## 🧪 Testing Strategy

### Test Phases
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - Service interaction testing
3. **OCR Regression Tests** - Document processing validation
4. **ERP Integration Tests** - External system connectivity
5. **Workflow Tests** - Business process validation
6. **Authentication Tests** - Security validation
7. **Code Quality Checks** - Linting, formatting, type checking

### Running Tests
```bash
# Run all tests with coverage
make test-coverage

# Run specific test file
docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/test_auth_system.py -v

# Run tests with specific markers
docker-compose -f docker-compose.dev.yml run --rm test-runner pytest -m "slow" -v

# Generate coverage report
docker-compose -f docker-compose.dev.yml run --rm test-runner pytest --cov=src --cov-report=html
```

### Test Data
- **Golden Dataset** - 50+ representative invoices for OCR testing
- **Mock ERP Adapters** - Simulated external system responses
- **Test Users & Companies** - Pre-configured test accounts
- **Audit Trail** - Complete test execution history

## 🔧 Development Workflow

### 1. Daily Development
```bash
# Start your day
make start

# Make code changes (auto-reload enabled)
# View logs in real-time
make logs-backend

# Run tests before committing
make test-cycle

# Stop when done
make stop
```

### 2. Adding New Features
```bash
# Create new migration
make migrate-create name=add_new_feature

# Run tests for new feature
make test-unit

# Check code quality
make lint
make type-check

# Run full test suite
make test
```

### 3. Debugging Issues
```bash
# Check service status
make status

# View specific service logs
make logs-backend
make logs-web
make logs-db

# Access service shells
make shell-backend
make shell-db

# Run health checks
make health
```

## 📊 Monitoring & Observability

### Health Endpoints
- **Backend Health**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Database Status**: Check via `make health`

### Logs & Debugging
```bash
# View all logs
make logs

# View specific service logs
make logs-backend
make logs-web
make logs-worker

# Follow logs in real-time
docker-compose -f docker-compose.dev.yml logs -f backend
```

### Performance Monitoring
- **Request Timing** - X-Process-Time headers
- **Database Queries** - SQLAlchemy query logging
- **OCR Processing** - Azure Form Recognizer metrics
- **Queue Monitoring** - Celery task status

## 🚨 Troubleshooting

### Common Issues

#### Docker Not Running
```bash
# Check Docker status
docker info

# Start Docker Desktop (Windows/Mac)
# Or start Docker service (Linux)
sudo systemctl start docker
```

#### Port Conflicts
```bash
# Check what's using ports
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Stop conflicting services or change ports in docker-compose.dev.yml
```

#### Database Connection Issues
```bash
# Check database status
make health

# Reset database
make db-reset

# Check database logs
make logs-db
```

#### Test Failures
```bash
# Run specific failing test
docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/test_specific.py -v

# Check test database
docker-compose -f docker-compose.dev.yml exec postgres_test psql -U postgres -d ai_erp_test
```

### Recovery Commands
```bash
# Complete reset
make clean
make setup

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend

# Rebuild and restart
make build
make start
```

## 🔐 Environment Configuration

### Environment Variables
The development environment uses these default settings:
- **Database**: PostgreSQL with test data
- **Redis**: Local Redis instance
- **OCR**: Mock OCR provider (no Azure credentials needed)
- **Stripe**: Test mode (no real payments)
- **JWT**: Development secret key

### Customizing Configuration
1. Create `.env` file in backend directory
2. Override specific variables as needed
3. Restart services: `make restart`

## 📚 Next Steps

### Phase 1: Core System Validation
- ✅ Environment setup
- ✅ Basic functionality testing
- ✅ OCR pipeline validation
- ✅ ERP integration testing

### Phase 2: Advanced Features
- 🚧 AI-powered fraud detection
- 🚧 Real-time processing
- 🚧 Advanced workflow engine
- 🚧 Multi-ERP adapters

### Phase 3: Production Readiness
- 🚧 Performance optimization
- 🚧 Security hardening
- 🚧 Monitoring & alerting
- 🚧 CI/CD pipeline

## 🤝 Getting Help

### Documentation
- **API Docs**: http://localhost:8000/docs
- **Master Prompt**: `MasterPromptDoc.md`
- **Build Script**: `BUILD_SCRIPT.md`
- **Contributing**: `CONTRIBUTING.md`

### Support
- Check logs: `make logs`
- Run diagnostics: `make health`
- Review test reports: Generated in `backend/test_report.md`
- Setup reports: Generated in `setup_report.md`

---

## 🎯 Success Criteria

Your development environment is ready when:
- ✅ All services start without errors
- ✅ Health checks pass: `make health`
- ✅ Tests pass: `make test`
- ✅ Coverage ≥85%: `make test-coverage`
- ✅ Code quality checks pass: `make lint`

**Happy coding! 🚀**



















