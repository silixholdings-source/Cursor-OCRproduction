#!/bin/bash
# Script to set up environment variables for AI ERP SaaS App

# Create backend .env file
cat > backend/.env << 'EOL'
# Application Configuration
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=development-secret-key-replace-in-production
JWT_SECRET=development-jwt-secret-replace-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_erp_saas
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_POOL_SIZE=10

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=*

# External Services
AZURE_FORM_RECOGNIZER_ENDPOINT=
AZURE_FORM_RECOGNIZER_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Observability
SENTRY_DSN=
OTEL_ENDPOINT=

# OCR Settings
OCR_PROVIDER=advanced
OCR_CONFIDENCE_THRESHOLD=0.8

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=[".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Feature Flags
ENABLE_PAYMENTS=true
ENABLE_SSO=false
ENABLE_SCIM=false
EOL

# Create web .env.local file
cat > web/.env.local << 'EOL'
# Frontend Environment Variables

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Authentication
NEXT_PUBLIC_JWT_SECRET=development-jwt-secret
NEXT_PUBLIC_REFRESH_TOKEN_SECRET=development-refresh-token-secret

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_AI_INSIGHTS=true
NEXT_PUBLIC_ENABLE_REAL_TIME=true

# External Services
NEXT_PUBLIC_SENTRY_DSN=

# Development
NEXT_PUBLIC_DEBUG_MODE=true
NEXT_PUBLIC_MOCK_DATA=true
EOL

echo "Environment files created successfully:"
echo "- backend/.env"
echo "- web/.env.local"
echo ""
echo "You can now run the application using Docker Compose:"
echo "npm run start:dev"

# Make the script executable
chmod +x setup-env.sh































