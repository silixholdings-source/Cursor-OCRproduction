# AI ERP SaaS Application Makefile
# Comprehensive development, testing, and deployment commands

.PHONY: help install start stop restart logs clean test test-unit test-integration test-e2e test-coverage lint format migrate seed build deploy

# Default target
help:
	@echo "AI ERP SaaS Application - Available Commands:"
	@echo ""
	@echo "Environment Setup:"
	@echo "  install          - Install dependencies and setup environment"
	@echo "  setup            - Initial setup (databases, migrations, seed data)"
	@echo ""
	@echo "Development:"
	@echo "  start            - Start all development services"
	@echo "  stop             - Stop all development services"
	@echo "  restart          - Restart all development services"
	@echo "  logs             - View logs from all services"
	@echo "  logs-backend     - View backend logs"
	@echo "  logs-web         - View web frontend logs"
	@echo "  logs-db          - View database logs"
	@echo ""
	@echo "Testing:"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e         - Run end-to-end tests"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-ocr         - Run OCR regression tests"
	@echo "  test-erp         - Run ERP integration tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             - Run linting checks"
	@echo "  format           - Format code automatically"
	@echo "  type-check       - Run type checking"
	@echo ""
	@echo "Database:"
	@echo "  migrate          - Run database migrations"
	@echo "  migrate-create   - Create new migration"
	@echo "  seed             - Seed database with test data"
	@echo "  db-reset         - Reset development database"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build            - Build all Docker images"
	@echo "  deploy           - Deploy to staging/production"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            - Clean up containers, volumes, and images"
	@echo "  status           - Show status of all services"
	@echo "  shell-backend    - Open shell in backend container"
	@echo "  shell-web        - Open shell in web container"
	@echo "  shell-db         - Open shell in database container"

# Check if Docker is running
check-docker:
	@if ! docker info > /dev/null 2>&1; then \
		echo "Error: Docker is not running. Please start Docker Desktop first."; \
		exit 1; \
	fi

# Install dependencies and setup environment
install: check-docker
	@echo "Installing dependencies and setting up environment..."
	docker-compose -f docker-compose.dev.yml build
	@echo "Installation complete!"

# Initial setup
setup: check-docker
	@echo "Setting up initial environment..."
	docker-compose -f docker-compose.dev.yml up -d postgres redis
	@echo "Waiting for database to be ready..."
	@sleep 10
	docker-compose -f docker-compose.dev.yml run --rm backend python -m alembic upgrade head
	docker-compose -f docker-compose.dev.yml run --rm backend python -c "
from src.core.database import engine
from src.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"
	@echo "Setup complete!"

# Start development environment
start: check-docker
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "Backend API: http://localhost:8000"
	@echo "Web Frontend: http://localhost:3000"
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Database: localhost:5432"
	@echo "Redis: localhost:6379"

# Stop development environment
stop: check-docker
	@echo "Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down
	@echo "Development environment stopped!"

# Restart development environment
restart: stop start

# View logs
logs: check-docker
	docker-compose -f docker-compose.dev.yml logs -f

logs-backend: check-docker
	docker-compose -f docker-compose.dev.yml logs -f backend

logs-web: check-docker
	docker-compose -f docker-compose.dev.yml logs -f web

logs-db: check-docker
	docker-compose -f docker-compose.dev.yml logs -f postgres

# Run tests
test: check-docker
	@echo "Running all tests..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner

test-unit: check-docker
	@echo "Running unit tests..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/ -v

test-integration: check-docker
	@echo "Running integration tests..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/integration/ -v

test-e2e: check-docker
	@echo "Running end-to-end tests..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/e2e/ -v

test-coverage: check-docker
	@echo "Running tests with coverage..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner pytest --cov=src --cov-report=html --cov-report=term-missing

test-ocr: check-docker
	@echo "Running OCR regression tests..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/test_ocr.py -v

test-erp: check-docker
	@echo "Running ERP integration tests..."
	docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/test_erp.py -v

# Code quality
lint: check-docker
	@echo "Running linting checks..."
	docker-compose -f docker-compose.dev.yml run --rm backend black --check src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm backend isort --check-only src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm backend flake8 src/ tests/
	@echo "Linting complete!"

format: check-docker
	@echo "Formatting code..."
	docker-compose -f docker-compose.dev.yml run --rm backend black src/ tests/
	docker-compose -f docker-compose.dev.yml run --rm backend isort src/ tests/
	@echo "Code formatting complete!"

type-check: check-docker
	@echo "Running type checks..."
	docker-compose -f docker-compose.dev.yml run --rm backend mypy src/
	@echo "Type checking complete!"

# Database operations
migrate: check-docker
	@echo "Running database migrations..."
	docker-compose -f docker-compose.dev.yml run --rm backend python -m alembic upgrade head

migrate-create: check-docker
	@if [ -z "$(name)" ]; then \
		echo "Usage: make migrate-create name=migration_name"; \
		exit 1; \
	fi
	docker-compose -f docker-compose.dev.yml run --rm backend python -m alembic revision --autogenerate -m "$(name)"

seed: check-docker
	@echo "Seeding database with test data..."
	docker-compose -f docker-compose.dev.yml run --rm backend python -c "
from src.services.audit import seed_test_data
seed_test_data()
print('Test data seeded successfully')
"

db-reset: check-docker
	@echo "Resetting development database..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up -d postgres redis
	@sleep 10
	$(MAKE) migrate
	$(MAKE) seed
	@echo "Database reset complete!"

# Build and deploy
build: check-docker
	@echo "Building Docker images..."
	docker-compose -f docker-compose.dev.yml build --no-cache
	@echo "Build complete!"

deploy: check-docker
	@echo "Deploying to staging..."
	@echo "Deployment commands will be implemented based on your infrastructure"
	@echo "Currently supporting: Docker Compose, Kubernetes, AWS ECS"

# Utilities
clean: check-docker
	@echo "Cleaning up containers, volumes, and images..."
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	@echo "Cleanup complete!"

status: check-docker
	@echo "Service Status:"
	docker-compose -f docker-compose.dev.yml ps

shell-backend: check-docker
	docker-compose -f docker-compose.dev.yml exec backend /bin/bash

shell-web: check-docker
	docker-compose -f docker-compose.dev.yml exec web /bin/bash

shell-db: check-docker
	docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d ai_erp_dev

# Health checks
health: check-docker
	@echo "Checking service health..."
	@echo "Backend API:"
	@curl -f http://localhost:8000/health || echo "Backend not responding"
	@echo "Database:"
	@docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres || echo "Database not ready"
	@echo "Redis:"
	@docker-compose -f docker-compose.dev.yml exec redis redis-cli ping || echo "Redis not responding"

# Development workflow
dev-workflow: check-docker
	@echo "Starting development workflow..."
	@echo "1. Starting services..."
	$(MAKE) start
	@echo "2. Running migrations..."
	$(MAKE) migrate
	@echo "3. Seeding test data..."
	$(MAKE) seed
	@echo "4. Running tests..."
	$(MAKE) test
	@echo "5. Starting development..."
	@echo "Development workflow complete! Services are running and ready."
	@echo "Backend: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:3000"

# Quick test cycle
test-cycle: check-docker
	@echo "Running quick test cycle..."
	$(MAKE) test-unit
	$(MAKE) test-integration
	$(MAKE) lint
	$(MAKE) type-check
	@echo "Quick test cycle complete!"
