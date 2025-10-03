#!/bin/bash

# 🚀 PRODUCTION DEPLOYMENT SCRIPT FOR AI ERP SAAS
# ⚠️ CRITICAL: Review and customize before deployment

set -e  # Exit on any error

echo "🚀 Starting AI ERP SaaS Production Deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Docker is installed and running"

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker Compose is available"

# Set deployment directory
DEPLOY_DIR="/opt/ai-erp-saas"
print_status "Deployment directory: $DEPLOY_DIR"

# Create deployment directory if it doesn't exist
if [ ! -d "$DEPLOY_DIR" ]; then
    print_status "Creating deployment directory..."
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $(whoami):$(whoami) "$DEPLOY_DIR"
fi

# Copy application files
print_status "Copying application files..."
cp -r . "$DEPLOY_DIR/"
cd "$DEPLOY_DIR"

# Generate secure secrets
print_status "Generating secure secrets..."
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
PAYSTACK_WEBHOOK_SECRET=$(openssl rand -base64 32)

print_warning "Generated secrets (save these securely):"
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET=$JWT_SECRET"
echo "PAYSTACK_WEBHOOK_SECRET=$PAYSTACK_WEBHOOK_SECRET"

# Create production environment file
print_status "Creating production environment file..."
cat > .env.production << EOF
# Production Environment Configuration
# Generated on $(date)

# Application
APP_NAME="AI ERP SaaS Platform"
APP_VERSION="1.0.0"
DEBUG=false
ENVIRONMENT=production

# Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database - UPDATE THESE VALUES
DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis - UPDATE THESE VALUES
REDIS_URL=redis://username:password@hostname:6379/0
REDIS_POOL_SIZE=20

# CORS - UPDATE THESE VALUES
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,app.yourdomain.com

# Security Headers
ENABLE_SECURITY_HEADERS=true
CSP_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"

# API Documentation
ENABLE_API_DOCS=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000
RATE_LIMIT_BURST=2000

# File Upload Security
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=.pdf,.jpg,.jpeg,.png,.tiff
UPLOAD_DIR=uploads

# Email Configuration - UPDATE THESE VALUES
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=CHANGE_ME_SMTP_PASSWORD
SMTP_TLS=true
SMTP_SSL=false

# Payment Processing - UPDATE THESE VALUES
PAYSTACK_SECRET_KEY=CHANGE_ME_PAYSTACK_SECRET_KEY
PAYSTACK_PUBLIC_KEY=CHANGE_ME_PAYSTACK_PUBLIC_KEY
PAYSTACK_WEBHOOK_SECRET=$PAYSTACK_WEBHOOK_SECRET

# Azure Form Recognizer - UPDATE THESE VALUES
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=CHANGE_ME_AZURE_FORM_RECOGNIZER_KEY

# Azure AD - UPDATE THESE VALUES
AZURE_CLIENT_ID=CHANGE_ME_AZURE_CLIENT_ID
AZURE_CLIENT_SECRET=CHANGE_ME_AZURE_CLIENT_SECRET
AZURE_TENANT_ID=CHANGE_ME_AZURE_TENANT_ID
AZURE_REDIRECT_URI=https://yourdomain.com/auth/azure/callback

# Monitoring
ENABLE_MONITORING=true
SENTRY_DSN=CHANGE_ME_SENTRY_DSN

# Logging
LOG_LEVEL=INFO

# Performance
MAX_WORKERS=8
WORKER_TIMEOUT=300

# Business Rules
AUTO_APPROVAL_LIMIT=10000.0
DUPLICATE_THRESHOLD=0.95
FRAUD_THRESHOLD=0.8

# ERP Integration
ERP_SYNC_ENABLED=true
ERP_SYNC_INTERVAL_MINUTES=30
ERP_RETRY_ATTEMPTS=3

# Multi-tenancy
ENABLE_MULTI_TENANCY=true
TENANT_ISOLATION_LEVEL=database

# Compliance
ENABLE_AUDIT_LOGGING=true
AUDIT_LOG_RETENTION_DAYS=2555
ENABLE_GDPR_COMPLIANCE=true

# Backup
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=90

# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_REAL_TIME_DASHBOARD=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_AUTOMATED_WORKFLOWS=true

# Notification
NOTIFICATION_ENABLED=true
NOTIFICATION_EMAIL_FROM=noreply@yourdomain.com

# Development Features - Disabled in production
ENABLE_DEBUG_TOOLBAR=false
ENABLE_SQL_LOGGING=false
EOF

print_warning "Production environment file created. Please update the following values:"
print_warning "- DATABASE_URL: Set to your PostgreSQL database"
print_warning "- REDIS_URL: Set to your Redis instance"
print_warning "- BACKEND_CORS_ORIGINS: Set to your domain(s)"
print_warning "- ALLOWED_HOSTS: Set to your domain(s)"
print_warning "- SMTP_*: Set to your email service"
print_warning "- PAYSTACK_*: Set to your Paystack credentials"
print_warning "- AZURE_*: Set to your Azure credentials"
print_warning "- SENTRY_DSN: Set to your Sentry DSN"

# Create production Docker Compose file
print_status "Creating production Docker Compose configuration..."
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.production
    container_name: ai-erp-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - .env.production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    networks:
      - ai-erp-network
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: ai-erp-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ai_erp_production
      POSTGRES_USER: ai_erp_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-change_me_secure_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ai-erp-network
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ai_erp_user -d ai_erp_production"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ai-erp-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD:-change_me_secure_password}
    volumes:
      - redis_data:/data
    networks:
      - ai-erp-network
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: ai-erp-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    networks:
      - ai-erp-network
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:

networks:
  ai-erp-network:
    driver: bridge
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Rate limiting
        limit_req zone=api burst=20 nodelay;

        # Health check endpoint (no rate limiting)
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300;
            proxy_connect_timeout 300;
            proxy_send_timeout 300;
        }

        # Login endpoint (stricter rate limiting)
        location /api/v1/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # All other requests
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # HTTPS server (uncomment and configure SSL certificates)
    # server {
    #     listen 443 ssl http2;
    #     server_name yourdomain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    #     ssl_prefer_server_ciphers off;
    #
    #     # Same location blocks as HTTP server
    # }
}
EOF

# Create production Dockerfile
print_status "Creating production Dockerfile..."
cat > Dockerfile.production << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p uploads logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
EOF

# Create SSL directory
print_status "Creating SSL directory..."
mkdir -p ssl

# Build and start services
print_status "Building Docker images..."
docker-compose -f docker-compose.production.yml build

print_status "Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 30

# Check service health
print_status "Checking service health..."
if docker-compose -f docker-compose.production.yml ps | grep -q "Up (healthy)"; then
    print_success "All services are running and healthy!"
else
    print_warning "Some services may not be healthy. Check logs:"
    docker-compose -f docker-compose.production.yml logs
fi

# Display deployment information
print_success "🎉 AI ERP SaaS has been deployed successfully!"
print_status "Deployment location: $DEPLOY_DIR"
print_status "Service URLs:"
print_status "  - Backend API: http://localhost:8000"
print_status "  - Health Check: http://localhost:8000/health"
print_status "  - Nginx Proxy: http://localhost:80"

print_warning "Next steps:"
print_warning "1. Update .env.production with your actual configuration values"
print_warning "2. Configure SSL certificates in the ssl/ directory"
print_warning "3. Update nginx.conf with your domain name"
print_warning "4. Set up monitoring and alerting"
print_warning "5. Configure backup procedures"
print_warning "6. Test all functionality thoroughly"

print_status "To view logs: docker-compose -f docker-compose.production.yml logs -f"
print_status "To stop services: docker-compose -f docker-compose.production.yml down"
print_status "To restart services: docker-compose -f docker-compose.production.yml restart"

print_success "Deployment completed successfully! 🚀"






