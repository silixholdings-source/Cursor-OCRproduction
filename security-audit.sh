#!/bin/bash

# AI ERP SaaS Security Audit Script
# Run this script before production deployment

set -e

echo "🔍 Starting Security Audit..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root - some checks may not be accurate"
fi

echo "📋 Checking Environment Configuration..."

# Check for production environment file
if [ -f ".env.production" ]; then
    print_status "Production environment file exists" 0
else
    print_status "Production environment file missing" 1
    echo "  Run: cp production.env.template .env.production"
fi

# Check for default secrets
if grep -q "CHANGE_THIS_TO_A_SECURE" .env.production 2>/dev/null; then
    print_status "Default secrets detected in production config" 1
    echo "  Update all SECRET_KEY and JWT_SECRET values"
else
    print_status "No default secrets found" 0
fi

# Check for debug mode
if grep -q "DEBUG=true" .env.production 2>/dev/null; then
    print_status "Debug mode enabled in production" 1
    echo "  Set DEBUG=false in production"
else
    print_status "Debug mode disabled" 0
fi

# Check for wildcard CORS
if grep -q 'ALLOWED_HOSTS=\["\*"\]' .env.production 2>/dev/null; then
    print_status "Wildcard CORS configuration detected" 1
    echo "  Restrict CORS to specific domains"
else
    print_status "CORS configuration appears secure" 0
fi

echo "🔐 Checking SSL Certificates..."

# Check for SSL certificates
if [ -f "ssl/fullchain.pem" ] && [ -f "ssl/privkey.pem" ]; then
    print_status "SSL certificates found" 0
    
    # Check certificate expiration
    EXPIRY=$(openssl x509 -in ssl/fullchain.pem -noout -dates | grep notAfter | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$EXPIRY" +%s 2>/dev/null)
    CURRENT_EPOCH=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_LEFT -lt 30 ]; then
        print_warning "SSL certificate expires in $DAYS_LEFT days"
    else
        print_status "SSL certificate valid for $DAYS_LEFT days" 0
    fi
else
    print_status "SSL certificates missing" 1
    echo "  Generate SSL certificates before deployment"
fi

echo "🐳 Checking Docker Configuration..."

# Check for production Docker Compose file
if [ -f "docker-compose.production.yml" ]; then
    print_status "Production Docker Compose file exists" 0
else
    print_status "Production Docker Compose file missing" 1
fi

# Check for non-root users in Dockerfiles
if grep -q "USER app" backend/Dockerfile.production 2>/dev/null; then
    print_status "Backend runs as non-root user" 0
else
    print_status "Backend may run as root user" 1
fi

if grep -q "USER nextjs" web/Dockerfile.production 2>/dev/null; then
    print_status "Frontend runs as non-root user" 0
else
    print_status "Frontend may run as root user" 1
fi

echo "🔒 Checking Security Headers..."

# Check Next.js security configuration
if grep -q "poweredByHeader: false" web/next.config.js 2>/dev/null; then
    print_status "X-Powered-By header disabled" 0
else
    print_status "X-Powered-By header not disabled" 1
fi

if grep -q "X-Frame-Options" web/next.config.js 2>/dev/null; then
    print_status "Security headers configured" 0
else
    print_status "Security headers missing" 1
fi

echo "🗄️ Checking Database Security..."

# Check for default database credentials
if grep -q "postgres:password" .env.production 2>/dev/null; then
    print_status "Default database credentials detected" 1
    echo "  Change default database passwords"
else
    print_status "Database credentials appear secure" 0
fi

# Check for SSL database connection
if grep -q "sslmode=require" .env.production 2>/dev/null; then
    print_status "Database SSL connection enabled" 0
else
    print_status "Database SSL connection not enforced" 1
fi

echo "📊 Checking Monitoring Configuration..."

# Check for monitoring setup
if [ -f "docker-compose.production.yml" ] && grep -q "prometheus" docker-compose.production.yml; then
    print_status "Monitoring stack configured" 0
else
    print_warning "Monitoring stack not configured"
fi

echo "🔍 Checking Application Security..."

# Check for rate limiting
if grep -q "rate_limit" backend/src 2>/dev/null; then
    print_status "Rate limiting implemented" 0
else
    print_status "Rate limiting not found" 1
fi

# Check for input validation
if find backend/src -name "*.py" -exec grep -l "validator\|validation" {} \; | grep -q .; then
    print_status "Input validation found" 0
else
    print_warning "Input validation may be missing"
fi

echo "🧪 Running Security Tests..."

# Check for security tools
if command -v bandit &> /dev/null; then
    echo "Running Bandit security scan..."
    cd backend && bandit -r src/ -f txt -q || print_warning "Bandit found potential issues"
    cd ..
else
    print_warning "Bandit not installed - run: pip install bandit"
fi

# Check for vulnerable dependencies
if command -v safety &> /dev/null; then
    echo "Running Safety dependency check..."
    cd backend && safety check --short-report || print_warning "Safety found vulnerable dependencies"
    cd ..
else
    print_warning "Safety not installed - run: pip install safety"
fi

echo "📋 Security Audit Summary:"
echo "=========================="

# Count issues
ISSUES=0

# Re-run critical checks and count failures
[ ! -f ".env.production" ] && ISSUES=$((ISSUES + 1))
[ -f ".env.production" ] && grep -q "CHANGE_THIS_TO_A_SECURE" .env.production && ISSUES=$((ISSUES + 1))
[ -f ".env.production" ] && grep -q "DEBUG=true" .env.production && ISSUES=$((ISSUES + 1))
[ -f ".env.production" ] && grep -q 'ALLOWED_HOSTS=\["\*"\]' .env.production && ISSUES=$((ISSUES + 1))
[ ! -f "ssl/fullchain.pem" ] && ISSUES=$((ISSUES + 1))
[ ! -f "docker-compose.production.yml" ] && ISSUES=$((ISSUES + 1))

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 Security audit passed! Ready for production deployment.${NC}"
    exit 0
else
    echo -e "${RED}❌ Security audit failed with $ISSUES critical issues.${NC}"
    echo "Please fix the issues above before deploying to production."
    exit 1
fi

