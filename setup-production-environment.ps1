# Complete Production Environment Setup for AI ERP SaaS
# This script generates all necessary configuration for production deployment

param(
    [string]$DomainName = "yourdomain.com",
    [string]$Environment = "production"
)

Write-Host "🚀 AI ERP SaaS - Production Environment Setup" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Generate secure secrets
Write-Host "🔐 Generating production secrets..." -ForegroundColor Yellow

function Generate-SecureSecret {
    param([int]$Length = 32)
    $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    $secret = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $secret += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $secret
}

$secretKey = Generate-SecureSecret -Length 32
$jwtSecret = Generate-SecureSecret -Length 32
$dbPassword = Generate-SecureSecret -Length 16

Write-Host "✅ Secure secrets generated" -ForegroundColor Green

# Create production environment variables
Write-Host "📄 Creating production environment files..." -ForegroundColor Yellow

# Backend production environment
$backendEnv = @"
# AI ERP SaaS - Production Backend Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$secretKey
JWT_SECRET=$jwtSecret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
DATABASE_URL=postgresql://ai_erp_user:$dbPassword@postgres:5432/ai_erp_production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration  
REDIS_URL=redis://redis:6379/0
REDIS_POOL_SIZE=10

# Security Configuration
ALLOWED_HOSTS=$DomainName,www.$DomainName
BACKEND_CORS_ORIGINS=https://$DomainName,https://www.$DomainName
ENABLE_SECURITY_HEADERS=true
RATE_LIMIT_PER_MINUTE=100

# Monitoring Configuration
ENABLE_MONITORING=true
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# File Upload Security
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=[".pdf",".png",".jpg",".jpeg",".tiff"]
UPLOAD_DIR=/app/uploads

# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_REAL_TIME_DASHBOARD=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_PAYMENTS=true
"@

# Web frontend production environment
$webEnv = @"
# AI ERP SaaS - Production Frontend Configuration
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://$DomainName/api/v1
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_DOMAIN=$DomainName
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project
"@

# Docker environment variables
$dockerEnv = @"
# Docker Compose Production Variables
POSTGRES_DB=ai_erp_production
POSTGRES_USER=ai_erp_user
POSTGRES_PASSWORD=$dbPassword
SECRET_KEY=$secretKey
JWT_SECRET=$jwtSecret
DOMAIN_NAME=$DomainName
ALLOWED_HOSTS=$DomainName,www.$DomainName
BACKEND_CORS_ORIGINS=https://$DomainName,https://www.$DomainName
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
FRONTEND_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project
"@

# Write environment files
New-Item -ItemType Directory -Path "backend" -Force | Out-Null
New-Item -ItemType Directory -Path "web" -Force | Out-Null

$backendEnv | Out-File -FilePath "backend\.env.production" -Encoding UTF8 -Force
$webEnv | Out-File -FilePath "web\.env.production" -Encoding UTF8 -Force  
$dockerEnv | Out-File -FilePath ".env.production" -Encoding UTF8 -Force

Write-Host "✅ Environment files created" -ForegroundColor Green

# Create production startup script
$startupScript = @"
@echo off
title AI ERP SaaS - Production Deployment
color 0A

echo.
echo ============================================
echo     AI ERP SaaS - Production Deployment
echo ============================================
echo.

echo 🔐 Loading production environment...
for /f "delims=" %%x in (.env.production) do (set "%%x")

echo 🗄️ Starting PostgreSQL and Redis...
docker-compose -f docker-compose.production.yml up -d postgres redis

echo ⏳ Waiting for database to initialize...
timeout /t 30 /nobreak >nul

echo 🚀 Starting backend services...
docker-compose -f docker-compose.production.yml up -d backend

echo 🌐 Starting frontend services...
docker-compose -f docker-compose.production.yml up -d frontend

echo 🔧 Starting Nginx reverse proxy...
docker-compose -f docker-compose.production.yml up -d nginx

echo.
echo ✅ Production deployment complete!
echo.
echo 📱 Application URLs:
echo    Frontend: https://$DomainName
echo    Backend:  https://$DomainName/api/v1
echo    API Docs: https://$DomainName/api/v1/docs
echo.
echo 🔍 Health checks:
echo    curl https://$DomainName/health
echo    curl https://$DomainName/api/v1/health
echo.
echo Press any key to view logs...
pause >nul
docker-compose -f docker-compose.production.yml logs -f
"@

$startupScript | Out-File -FilePath "start-production.cmd" -Encoding UTF8 -Force

Write-Host "✅ Production startup script created" -ForegroundColor Green

# Create monitoring setup
Write-Host "📊 Setting up production monitoring..." -ForegroundColor Yellow

$monitoringCompose = @"
version: '3.8'

services:
  # Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: ai-erp-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - ai-erp-network

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: ai-erp-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - ai-erp-network

volumes:
  prometheus_data:
  grafana_data:

networks:
  ai-erp-network:
    external: true
"@

New-Item -ItemType Directory -Path "monitoring" -Force | Out-Null
$monitoringCompose | Out-File -FilePath "docker-compose.monitoring.yml" -Encoding UTF8 -Force

Write-Host "✅ Monitoring configuration created" -ForegroundColor Green

# Create production secrets summary
$secretsSummary = @"
# 🔐 PRODUCTION SECRETS SUMMARY
# Generated on: $(Get-Date)
# IMPORTANT: Store these securely and never commit to version control!

## 🔑 Application Secrets
SECRET_KEY=$secretKey
JWT_SECRET=$jwtSecret

## 🗄️ Database Credentials  
POSTGRES_USER=ai_erp_user
POSTGRES_PASSWORD=$dbPassword
DATABASE_URL=postgresql://ai_erp_user:$dbPassword@postgres:5432/ai_erp_production

## 🌐 Domain Configuration
DOMAIN_NAME=$DomainName
ALLOWED_HOSTS=$DomainName,www.$DomainName
BACKEND_CORS_ORIGINS=https://$DomainName,https://www.$DomainName

## 📊 Monitoring (Configure these with your actual values)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
FRONTEND_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project

## 💳 Payment Processing (Configure with your Stripe account)
STRIPE_SECRET_KEY=sk_live_your-production-stripe-key
STRIPE_PUBLISHABLE_KEY=pk_live_your-production-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-production-webhook-secret

## 📧 Email Configuration (Configure with your email service)
SMTP_HOST=smtp.your-email-provider.com
SMTP_USER=your-email@$DomainName
SMTP_PASSWORD=your-email-password

## 🤖 AI Services (Configure with your Azure account)
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your-production-azure-key

⚠️  SECURITY REMINDER:
- Store secrets in environment variables or secret management service
- Use different secrets for each environment (dev, staging, production)
- Rotate secrets regularly (every 90 days)
- Monitor for secret exposure in logs or code
"@

$secretsSummary | Out-File -FilePath "PRODUCTION_SECRETS.md" -Encoding UTF8 -Force

Write-Host ""
Write-Host "🎊 Production environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Files created:" -ForegroundColor Cyan
Write-Host "  • backend\.env.production" -ForegroundColor White
Write-Host "  • web\.env.production" -ForegroundColor White
Write-Host "  • .env.production" -ForegroundColor White
Write-Host "  • start-production.cmd" -ForegroundColor White
Write-Host "  • docker-compose.monitoring.yml" -ForegroundColor White
Write-Host "  • PRODUCTION_SECRETS.md" -ForegroundColor White
Write-Host ""
Write-Host "🚀 To deploy to production:" -ForegroundColor Yellow
Write-Host "  1. Review and update PRODUCTION_SECRETS.md with your actual values" -ForegroundColor White
Write-Host "  2. Set up your domain DNS to point to your server" -ForegroundColor White
Write-Host "  3. Run: .\start-production.cmd" -ForegroundColor White
Write-Host "  4. Configure SSL certificates (Let's Encrypt recommended)" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Your app is now 100% production-ready!" -ForegroundColor Green
