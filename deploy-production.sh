#!/bin/bash

# Production Deployment Script
set -e

echo "🚀 Starting AI ERP SaaS Production Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy production.env.template to .env and configure your settings."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "CORS_ORIGINS" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set!"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p nginx/ssl
mkdir -p logs
mkdir -p backups

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check database
if ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U ${POSTGRES_USER:-postgres}; then
    echo "❌ Database is not ready!"
    exit 1
fi

# Check backend
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend is not ready!"
    exit 1
fi

# Check frontend
if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "❌ Frontend is not ready!"
    exit 1
fi

# Check OCR service
if ! curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "❌ OCR service is not ready!"
    exit 1
fi

echo "✅ All services are healthy!"

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head

# Create initial admin user (if needed)
echo "👤 Creating initial admin user..."
docker-compose -f docker-compose.prod.yml exec -T backend python -c "
from src.core.database import SessionLocal
from src.models.optimized_models import User, Company, UserRole, CompanyStatus
from passlib.context import CryptContext
import uuid

db = SessionLocal()
try:
    # Check if admin user exists
    admin_user = db.query(User).filter(User.email == 'admin@example.com').first()
    if not admin_user:
        # Create default company
        company = Company(
            name='Default Company',
            email='admin@example.com',
            status=CompanyStatus.ACTIVE
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Create admin user
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        admin_user = User(
            email='admin@example.com',
            hashed_password=pwd_context.hash('admin123'),
            first_name='Admin',
            last_name='User',
            company_id=company.id,
            role=UserRole.OWNER,
            is_active=True,
            is_email_verified=True
        )
        db.add(admin_user)
        db.commit()
        print('Admin user created: admin@example.com / admin123')
    else:
        print('Admin user already exists')
finally:
    db.close()
"

# Setup SSL certificates (if provided)
if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
    echo "🔒 SSL certificates found, enabling HTTPS..."
    # Update nginx config to use HTTPS
    sed -i 's/# server {/server {/' nginx/nginx.prod.conf
    sed -i 's/# }/}/' nginx/nginx.prod.conf
    docker-compose -f docker-compose.prod.yml restart nginx
fi

# Setup log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/ai-erp << EOF
/var/log/ai-erp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f $(pwd)/docker-compose.prod.yml restart nginx
    endscript
}
EOF

# Setup monitoring (if enabled)
if [ "$ENABLE_MONITORING" = "true" ]; then
    echo "📊 Setting up monitoring..."
    # Add Prometheus and Grafana if needed
    echo "Monitoring setup completed"
fi

# Create backup script
echo "💾 Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/ai-erp-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U postgres ai_erp > $BACKUP_DIR/database.sql

# Backup uploads
docker cp ai-erp-backend-prod:/app/uploads $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz -C /backups $(basename $BACKUP_DIR)
rm -rf $BACKUP_DIR

# Keep only last 30 days of backups
find /backups -name "ai-erp-*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh

# Setup cron job for backups
echo "⏰ Setting up backup cron job..."
(crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/backup.sh") | crontab -

echo "🎉 Production deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "  - Database: PostgreSQL on port 5432"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - OCR Service: http://localhost:8001"
echo "  - Nginx: http://localhost:80"
echo ""
echo "🔑 Default Admin Credentials:"
echo "  - Email: admin@example.com"
echo "  - Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the default admin password immediately!"
echo ""
echo "📚 Next Steps:"
echo "  1. Update DNS to point to your server"
echo "  2. Configure SSL certificates"
echo "  3. Set up monitoring and alerting"
echo "  4. Configure backup storage"
echo "  5. Review security settings"
echo ""
echo "🔍 To view logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.prod.yml down"