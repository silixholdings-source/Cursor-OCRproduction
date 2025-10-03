#!/bin/bash
# Complete Production Deployment Script for AI ERP SaaS
# This script handles the full production deployment with all security and monitoring

set -e  # Exit on any error

echo "🚀 AI ERP SaaS - Complete Production Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if required environment variables are set
required_vars=("SECRET_KEY" "JWT_SECRET" "POSTGRES_PASSWORD" "DOMAIN_NAME")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set${NC}"
        echo -e "${YELLOW}Please set: export $var=your_value${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Generate SSL certificates (Let's Encrypt simulation)
echo -e "${BLUE}🔐 Setting up SSL certificates...${NC}"
mkdir -p ssl
# In production, use Let's Encrypt:
# certbot certonly --webroot -w /var/www/html -d $DOMAIN_NAME -d www.$DOMAIN_NAME

# For demo, create self-signed certificates
if [ ! -f ssl/fullchain.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/privkey.pem \
        -out ssl/fullchain.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN_NAME}"
    echo -e "${GREEN}✅ SSL certificates created${NC}"
fi

# Create production environment files
echo -e "${BLUE}📄 Creating production environment files...${NC}"

# Backend environment
cat > backend/.env.production << EOF
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=${SECRET_KEY}
JWT_SECRET=${JWT_SECRET}
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/ai_erp_saas
REDIS_URL=redis://redis:6379
ALLOWED_HOSTS=${DOMAIN_NAME},www.${DOMAIN_NAME}
BACKEND_CORS_ORIGINS=https://${DOMAIN_NAME},https://www.${DOMAIN_NAME}
SENTRY_DSN=${SENTRY_DSN:-}
LOG_LEVEL=INFO
ENABLE_MONITORING=true
RATE_LIMIT_PER_MINUTE=100
MAX_FILE_SIZE_MB=10
EOF

# Frontend environment
cat > web/.env.production << EOF
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://${DOMAIN_NAME}/api/v1
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_SENTRY_DSN=${FRONTEND_SENTRY_DSN:-}
EOF

echo -e "${GREEN}✅ Environment files created${NC}"

# Build production images
echo -e "${BLUE}🏗️ Building production images...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

# Start database and Redis first
echo -e "${BLUE}🗄️ Starting database services...${NC}"
docker-compose -f docker-compose.production.yml up -d postgres redis

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 30

# Run database migrations
echo -e "${BLUE}📊 Running database migrations...${NC}"
docker-compose -f docker-compose.production.yml exec -T postgres psql -U postgres -d ai_erp_saas << EOF
-- Create production database schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    company_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    tier VARCHAR(50) DEFAULT 'starter',
    status VARCHAR(50) DEFAULT 'active',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(100) NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    invoice_date DATE NOT NULL,
    due_date DATE,
    status VARCHAR(50) DEFAULT 'pending',
    company_id UUID NOT NULL,
    user_id UUID NOT NULL,
    file_path VARCHAR(500),
    ocr_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_invoices_company_id ON invoices(company_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);

-- Insert demo data
INSERT INTO companies (id, name, industry, tier) 
VALUES ('123e4567-e89b-12d3-a456-426614174000', 'Demo Company', 'Technology', 'professional')
ON CONFLICT DO NOTHING;

INSERT INTO users (id, email, hashed_password, name, role, company_id, is_verified)
VALUES ('123e4567-e89b-12d3-a456-426614174001', 'demo@example.com', 
        '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/yCyJL.2Pu', 
        'Demo User', 'admin', '123e4567-e89b-12d3-a456-426614174000', true)
ON CONFLICT DO NOTHING;
EOF

echo -e "${GREEN}✅ Database migrations completed${NC}"

# Start all services
echo -e "${BLUE}🚀 Starting all production services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 60

# Health check
echo -e "${BLUE}🔍 Running production health checks...${NC}"

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    docker-compose -f docker-compose.production.yml logs backend
    exit 1
fi

# Check frontend health
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend health check passed${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
    docker-compose -f docker-compose.production.yml logs frontend
    exit 1
fi

# Check nginx health
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx health check passed${NC}"
else
    echo -e "${YELLOW}⚠️ Nginx not responding (may need SSL setup)${NC}"
fi

echo ""
echo -e "${GREEN}🎉 PRODUCTION DEPLOYMENT COMPLETE!${NC}"
echo ""
echo -e "${BLUE}📱 Application URLs:${NC}"
echo -e "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   Nginx:    ${GREEN}http://localhost${NC}"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "   View logs:    ${YELLOW}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo -e "   Stop services: ${YELLOW}docker-compose -f docker-compose.production.yml down${NC}"
echo -e "   Restart:      ${YELLOW}docker-compose -f docker-compose.production.yml restart${NC}"
echo ""
echo -e "${GREEN}🎯 Your AI ERP SaaS is now running in production mode!${NC}"
