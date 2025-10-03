#!/bin/bash

# AI ERP SaaS Production Environment Setup Script
# This script helps you set up the production environment variables

set -e

echo "🔧 Setting up AI ERP SaaS Production Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_question() {
    echo -e "${BLUE}[QUESTION]${NC} $1"
}

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        eval "$var_name=\${input:-$default}"
    else
        read -p "$prompt: " input
        eval "$var_name=\"$input\""
    fi
}

# Function to generate random password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate random secret
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/"
}

print_status "This script will help you set up the production environment variables."
print_warning "Make sure you have the following information ready:"
print_warning "- Production database credentials"
print_warning "- Production Redis credentials"
print_warning "- Stripe production keys"
print_warning "- Azure Form Recognizer production credentials"
print_warning "- Your production domain name"
print_warning "- Email service credentials"
print_warning "- Sentry DSN for error tracking"

echo
read -p "Press Enter to continue..."

# Database configuration
echo
print_status "=== DATABASE CONFIGURATION ==="
prompt_with_default "PostgreSQL host" "localhost" "POSTGRES_HOST"
prompt_with_default "PostgreSQL port" "5432" "POSTGRES_PORT"
prompt_with_default "PostgreSQL database name" "ai_erp_production" "POSTGRES_DB"
prompt_with_default "PostgreSQL username" "ai_erp_user" "POSTGRES_USER"
prompt_with_default "PostgreSQL password" "$(generate_password)" "POSTGRES_PASSWORD"

# Redis configuration
echo
print_status "=== REDIS CONFIGURATION ==="
prompt_with_default "Redis host" "localhost" "REDIS_HOST"
prompt_with_default "Redis port" "6379" "REDIS_PORT"
prompt_with_default "Redis password" "$(generate_password)" "REDIS_PASSWORD"

# Domain configuration
echo
print_status "=== DOMAIN CONFIGURATION ==="
prompt_with_default "Production domain (without https://)" "" "PRODUCTION_DOMAIN"
prompt_with_default "API subdomain" "api" "API_SUBDOMAIN"

# Stripe configuration
echo
print_status "=== STRIPE CONFIGURATION ==="
print_warning "Get these from your Stripe Dashboard: https://dashboard.stripe.com/apikeys"
prompt_with_default "Stripe Secret Key (sk_live_...)" "" "STRIPE_SECRET_KEY"
prompt_with_default "Stripe Publishable Key (pk_live_...)" "" "STRIPE_PUBLISHABLE_KEY"
prompt_with_default "Stripe Webhook Secret (whsec_...)" "" "STRIPE_WEBHOOK_SECRET"

# Azure Form Recognizer configuration
echo
print_status "=== AZURE FORM RECOGNIZER CONFIGURATION ==="
print_warning "Get these from your Azure Portal: https://portal.azure.com"
prompt_with_default "Azure Form Recognizer Endpoint" "" "AZURE_FORM_RECOGNIZER_ENDPOINT"
prompt_with_default "Azure Form Recognizer Key" "" "AZURE_FORM_RECOGNIZER_KEY"

# Email configuration
echo
print_status "=== EMAIL CONFIGURATION ==="
prompt_with_default "SMTP Host" "" "SMTP_HOST"
prompt_with_default "SMTP Port" "587" "SMTP_PORT"
prompt_with_default "SMTP Username" "" "SMTP_USER"
prompt_with_default "SMTP Password" "" "SMTP_PASSWORD"
prompt_with_default "From Email Address" "noreply@$PRODUCTION_DOMAIN" "NOTIFICATION_EMAIL_FROM"

# Monitoring configuration
echo
print_status "=== MONITORING CONFIGURATION ==="
prompt_with_default "Sentry DSN (optional)" "" "SENTRY_DSN"
prompt_with_default "OpenTelemetry Endpoint (optional)" "" "OTEL_ENDPOINT"

# Generate secure secrets
print_status "Generating secure secrets..."
SECRET_KEY=$(generate_secret)
JWT_SECRET=$(generate_secret)

# Create production environment file
print_status "Creating production environment file..."

cat > .env.production << EOF
# AI ERP SaaS Production Environment
# Generated on $(date)

# Application Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$SECRET_KEY
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://:$REDIS_PASSWORD@$REDIS_HOST:$REDIS_PORT
REDIS_POOL_SIZE=10

# CORS Configuration
BACKEND_CORS_ORIGINS=https://$PRODUCTION_DOMAIN,https://www.$PRODUCTION_DOMAIN
ALLOWED_HOSTS=["$PRODUCTION_DOMAIN", "www.$PRODUCTION_DOMAIN"]

# External Services
AZURE_FORM_RECOGNIZER_ENDPOINT=$AZURE_FORM_RECOGNIZER_ENDPOINT
AZURE_FORM_RECOGNIZER_KEY=$AZURE_FORM_RECOGNIZER_KEY

# Stripe Configuration
STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=$STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET

# Email Configuration
SMTP_HOST=$SMTP_HOST
SMTP_PORT=$SMTP_PORT
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASSWORD
SMTP_TLS=true
SMTP_SSL=false
NOTIFICATION_EMAIL_FROM=$NOTIFICATION_EMAIL_FROM

# Observability
SENTRY_DSN=$SENTRY_DSN
OTEL_ENDPOINT=$OTEL_ENDPOINT

# OCR Settings
OCR_PROVIDER=azure
OCR_CONFIDENCE_THRESHOLD=0.8

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=[".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
UPLOAD_DIR=/var/uploads

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Security Headers
ENABLE_SECURITY_HEADERS=true
CSP_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com; frame-src https://js.stripe.com;

# Feature Flags
ENABLE_PAYMENTS=true
ENABLE_SSO=false
ENABLE_SCIM=false
ENABLE_AI_INSIGHTS=true
ENABLE_REAL_TIME_DASHBOARD=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_AUTOMATED_WORKFLOWS=true

# Monitoring
ENABLE_MONITORING=true
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_ERROR_REPORTING=true
LOG_LEVEL=INFO

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30

# Multi-tenancy
ENABLE_MULTI_TENANCY=true
TENANT_ISOLATION_LEVEL=database

# Compliance
ENABLE_AUDIT_LOGGING=true
AUDIT_LOG_RETENTION_DAYS=365
ENABLE_GDPR_COMPLIANCE=true

# Performance
MAX_WORKERS=4
WORKER_TIMEOUT=300
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE=1000
EOF

print_status "✅ Production environment file created: .env.production"

# Create environment variables for Docker Compose
print_status "Creating Docker Compose environment file..."

cat > .env.docker << EOF
# Docker Compose Environment Variables
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
PRODUCTION_DOMAIN=$PRODUCTION_DOMAIN
EOF

print_status "✅ Docker Compose environment file created: .env.docker"

# Update nginx configuration with domain
print_status "Updating Nginx configuration with your domain..."

sed -i "s/your-domain.com/$PRODUCTION_DOMAIN/g" nginx.production.conf
sed -i "s/your-domain.com/$PRODUCTION_DOMAIN/g" docker-compose.production.yml

print_status "✅ Nginx configuration updated"

print_status "🎉 Production environment setup completed!"
print_status ""
print_warning "⚠️  IMPORTANT NEXT STEPS:"
print_warning "1. Review the generated .env.production file"
print_warning "2. Update the domain in nginx.production.conf and docker-compose.production.yml"
print_warning "3. Obtain real SSL certificates and replace the self-signed ones"
print_warning "4. Run: chmod +x deploy-production.sh"
print_warning "5. Run: ./deploy-production.sh"
print_warning "6. Test all functionality thoroughly"
print_warning "7. Set up monitoring and alerting"
print_warning "8. Configure backup procedures"

print_status ""
print_status "Files created:"
print_status "- .env.production (production environment variables)"
print_status "- .env.docker (Docker Compose environment variables)"
print_status "- nginx.production.conf (updated with your domain)"
print_status "- docker-compose.production.yml (updated with your domain)"

