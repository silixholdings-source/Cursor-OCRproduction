# Makefile for FastAPI backend development

.PHONY: help install test test-unit test-integration test-performance test-coverage lint format type-check clean run dev

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-prod:  ## Install production dependencies only
	pip install -r requirements.txt

test:  ## Run all tests
	python run_tests.py --all --coverage

test-unit:  ## Run unit tests only
	python run_tests.py --unit --coverage

test-integration:  ## Run integration tests only
	python run_tests.py --integration --coverage

test-performance:  ## Run performance tests only
	python run_tests.py --performance

test-coverage:  ## Run tests with HTML coverage report
	python run_tests.py --all --coverage --html

test-watch:  ## Run tests in watch mode
	python -m pytest tests/ -f

test-parallel:  ## Run tests in parallel
	python run_tests.py --all --parallel 4

lint:  ## Run linting
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	black --check src tests
	isort --check-only src tests

format:  ## Format code
	black src tests
	isort src tests

type-check:  ## Run type checking
	mypy src --ignore-missing-imports

security:  ## Run security checks
	bandit -r src -f json -o bandit-report.json

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf test.db
	rm -rf bandit-report.json

run:  ## Run the application
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

dev:  ## Run in development mode with auto-reload
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

migrate:  ## Run database migrations
	alembic upgrade head

migrate-create:  ## Create a new migration
	alembic revision --autogenerate -m "$(MESSAGE)"

migrate-downgrade:  ## Downgrade database
	alembic downgrade -1

db-reset:  ## Reset database
	rm -f test.db
	alembic upgrade head

docker-build:  ## Build Docker image
	docker build -t ai-erp-backend .

docker-run:  ## Run Docker container
	docker run -p 8000:8000 ai-erp-backend

docker-test:  ## Run tests in Docker
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

ci:  ## Run CI pipeline locally
	make clean
	make install
	make lint
	make type-check
	make test
	make security

pre-commit:  ## Run pre-commit checks
	make format
	make lint
	make type-check
	make test-unit

# Development shortcuts
dev-setup:  ## Setup development environment
	make install
	make migrate
	make test

quick-test:  ## Quick test run
	python run_tests.py --unit --verbose

full-test:  ## Full test suite with all checks
	make clean
	make install
	make format
	make lint
	make type-check
	make test
	make security









