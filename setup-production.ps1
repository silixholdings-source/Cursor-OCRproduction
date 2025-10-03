# PowerShell script to set up production environment for AI ERP SaaS

Write-Host "🚀 AI ERP SaaS - Production Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Generate secure secrets
Write-Host "🔐 Generating secure secrets..." -ForegroundColor Yellow
$secretKey = [System.Web.Security.Membership]::GeneratePassword(32, 8)
$jwtSecret = [System.Web.Security.Membership]::GeneratePassword(32, 8)

Write-Host "✅ Secrets generated successfully" -ForegroundColor Green

# Create production environment content
$productionEnvContent = @"
# AI ERP SaaS - Production Environment (Generated $(Get-Date))
# CRITICAL: Review and update all placeholder values before deployment

# Application Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$secretKey
JWT_SECRET=$jwtSecret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration - REPLACE WITH PRODUCTION VALUES
DATABASE_URL=postgresql://username:password@your-production-db:5432/ai_erp_production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration - REPLACE WITH PRODUCTION VALUES
REDIS_URL=redis://your-production-redis:6379
REDIS_POOL_SIZE=10

# CORS Configuration - REPLACE WITH YOUR DOMAIN
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# External Services - REPLACE WITH PRODUCTION CREDENTIALS
AZURE_FORM_RECOGNIZER_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=your-production-azure-key
STRIPE_SECRET_KEY=sk_live_your-production-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-production-webhook-secret

# Email Configuration - REPLACE WITH YOUR EMAIL SERVICE
SMTP_HOST=smtp.your-email-provider.com
SMTP_PORT=587
SMTP_USER=your-email@yourdomain.com
SMTP_PASSWORD=your-email-password
SMTP_TLS=true

# Monitoring - REPLACE WITH YOUR MONITORING SERVICES
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project
OTEL_ENDPOINT=http://your-otel-collector:4317
ENABLE_MONITORING=true
LOG_LEVEL=INFO

# Security Settings
ENABLE_SECURITY_HEADERS=true
RATE_LIMIT_PER_MINUTE=100
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=[".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_REAL_TIME_DASHBOARD=true
ENABLE_ADVANCED_ANALYTICS=true
ENABLE_PAYMENTS=true
"@

# Write production environment file
$productionEnvContent | Out-File -FilePath "backend/.env.production" -Encoding utf8 -Force

Write-Host "📄 Created backend/.env.production" -ForegroundColor Green

# Create web production environment
$webProductionEnvContent = @"
# Web Frontend - Production Environment
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project
"@

$webProductionEnvContent | Out-File -FilePath "web/.env.production" -Encoding utf8 -Force

Write-Host "📄 Created web/.env.production" -ForegroundColor Green

# Create production deployment checklist
$checklistContent = @"
# 🚀 PRODUCTION DEPLOYMENT CHECKLIST

## ✅ BEFORE DEPLOYING TO PRODUCTION:

### 1. 🔐 Security Configuration
- [ ] Replace SECRET_KEY with strong 32-character secret
- [ ] Replace JWT_SECRET with strong 32-character secret  
- [ ] Update ALLOWED_HOSTS with your actual domain
- [ ] Update BACKEND_CORS_ORIGINS with your actual domain
- [ ] Set up SSL certificates (HTTPS)

### 2. 🗄️ Database Setup
- [ ] Set up PostgreSQL production database
- [ ] Update DATABASE_URL with production credentials
- [ ] Run database migrations
- [ ] Set up automated backups

### 3. 🔧 External Services
- [ ] Configure Azure Form Recognizer for OCR
- [ ] Set up Stripe for payments (live keys)
- [ ] Configure SMTP for email notifications
- [ ] Set up Sentry for error tracking

### 4. 🏗️ Infrastructure
- [ ] Set up Redis for caching and sessions
- [ ] Configure load balancer
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation

### 5. 🧪 Testing
- [ ] Run security penetration tests
- [ ] Perform load testing
- [ ] Test backup and recovery procedures
- [ ] Verify all integrations work

## 🎯 GENERATED SECRETS:
SECRET_KEY: $secretKey
JWT_SECRET: $jwtSecret

⚠️  IMPORTANT: Keep these secrets secure and never commit them to version control!
"@

$checklistContent | Out-File -FilePath "PRODUCTION_DEPLOYMENT_CHECKLIST.md" -Encoding utf8 -Force

Write-Host "📋 Created PRODUCTION_DEPLOYMENT_CHECKLIST.md" -ForegroundColor Green

Write-Host ""
Write-Host "🎊 Production setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Files created:" -ForegroundColor Cyan
Write-Host "  • backend/.env.production" -ForegroundColor White
Write-Host "  • web/.env.production" -ForegroundColor White  
Write-Host "  • PRODUCTION_DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Review and update all placeholder values in .env.production files" -ForegroundColor White
Write-Host "  2. Set up PostgreSQL and Redis infrastructure" -ForegroundColor White
Write-Host "  3. Configure external services (Azure, Stripe, SMTP)" -ForegroundColor White
Write-Host "  4. Follow the deployment checklist" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Your app is now ready for production deployment!" -ForegroundColor Green
