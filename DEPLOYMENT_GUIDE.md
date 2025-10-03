# 🚀 Production Deployment Guide

## ⚠️ CRITICAL SECURITY REQUIREMENTS

**DO NOT DEPLOY TO PRODUCTION WITHOUT COMPLETING ALL SECURITY STEPS BELOW**

---

## 🔐 Pre-Deployment Security Checklist

### 1. **Generate Secure Secrets**
```bash
# Generate secure secrets (run these commands and save the output)
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 32  # For JWT_SECRET
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD
openssl rand -base64 32  # For GRAFANA_PASSWORD
```

### 2. **Update Production Environment**
```bash
# Copy and customize the production template
cp production.env.template .env.production

# Edit .env.production with your secure secrets
nano .env.production
```

**Required Changes in `.env.production`:**
- ✅ Change all `CHANGE_THIS_TO_A_SECURE_*` values
- ✅ Update domain names from `yourdomain.com`
- ✅ Set strong database passwords
- ✅ Configure production API keys
- ✅ Set up monitoring credentials

### 3. **SSL Certificate Setup**
```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificates for testing (replace with real certificates)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Copy certificates to all required locations
cp ssl/fullchain.pem ssl/postgres.crt
cp ssl/privkey.pem ssl/postgres.key
cp ssl/fullchain.pem ssl/redis.crt
cp ssl/privkey.pem ssl/redis.key
cp ssl/fullchain.pem ssl/backend.crt
cp ssl/privkey.pem ssl/backend.key
cp ssl/fullchain.pem ssl/ca.crt
```

### 4. **Database Security**
```bash
# Create production database user
docker exec -it ai-erp-postgres-prod psql -U postgres -c "
CREATE USER ai_erp_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';
CREATE DATABASE ai_erp_production OWNER ai_erp_user;
GRANT ALL PRIVILEGES ON DATABASE ai_erp_production TO ai_erp_user;
"
```

---

## 🏗️ Deployment Steps

### 1. **Build Production Images**
```bash
# Build all production images
docker-compose -f docker-compose.production.yml build --no-cache

# Verify images were built
docker images | grep ai-erp
```

### 2. **Start Production Services**
```bash
# Start production environment
docker-compose -f docker-compose.production.yml up -d

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### 3. **Run Database Migrations**
```bash
# Run database migrations
docker exec -it ai-erp-backend-prod alembic upgrade head

# Verify database setup
docker exec -it ai-erp-backend-prod python -c "
from src.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    print(f'Users table exists with {result.scalar()} records')
"
```

### 4. **Health Checks**
```bash
# Check all services are healthy
curl -f https://yourdomain.com/health
curl -f https://yourdomain.com/api/v1/health
curl -f https://admin.yourdomain.com/health

# Check monitoring
curl -f http://yourdomain.com:9090  # Prometheus
curl -f http://yourdomain.com:3001  # Grafana
```

---

## 🔍 Post-Deployment Verification

### 1. **Security Verification**
```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check security headers
curl -I https://yourdomain.com

# Verify CORS restrictions
curl -H "Origin: https://malicious-site.com" https://yourdomain.com/api/v1/health
```

### 2. **Performance Testing**
```bash
# Install k6 for load testing
curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xvz --strip-components 1

# Run basic load test
k6 run --vus 10 --duration 30s load-test.js
```

### 3. **Monitoring Setup**
```bash
# Access Grafana (default: admin / your-grafana-password)
open https://yourdomain.com:3001

# Check Prometheus metrics
curl https://yourdomain.com:9090/metrics

# Verify application logs
docker-compose -f docker-compose.production.yml logs backend | tail -100
```

---

## 🚨 Security Hardening

### 1. **Firewall Configuration**
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (redirect to HTTPS)
ufw allow 443/tcp   # HTTPS
ufw deny 5432/tcp   # PostgreSQL (internal only)
ufw deny 6379/tcp   # Redis (internal only)
ufw deny 8000/tcp   # Backend API (internal only)
ufw deny 3000/tcp   # Frontend (internal only)
ufw enable
```

### 2. **Database Security**
```bash
# Remove default postgres user access
docker exec -it ai-erp-postgres-prod psql -U postgres -c "
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO ai_erp_user;
GRANT CREATE ON SCHEMA public TO ai_erp_user;
"
```

### 3. **Container Security**
```bash
# Verify containers run as non-root
docker exec ai-erp-backend-prod id
docker exec ai-erp-web-prod id
docker exec ai-erp-postgres-prod id

# Check read-only filesystems
docker exec ai-erp-backend-prod touch /tmp/test || echo "Read-only confirmed"
```

---

## 📊 Monitoring & Alerting

### 1. **Set Up Alerts**
- Configure Grafana alerts for:
  - High CPU usage (>80%)
  - High memory usage (>90%)
  - Database connection failures
  - SSL certificate expiration
  - Failed login attempts

### 2. **Log Management**
```bash
# Set up log rotation
cat > /etc/logrotate.d/ai-erp << EOF
/var/log/ai-erp/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
```

### 3. **Backup Strategy**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ai-erp"

mkdir -p $BACKUP_DIR

# Database backup
docker exec ai-erp-postgres-prod pg_dump -U ai_erp_user ai_erp_production > $BACKUP_DIR/db_backup_$DATE.sql

# Redis backup
docker exec ai-erp-redis-prod redis-cli --rdb /data/dump_$DATE.rdb
docker cp ai-erp-redis-prod:/data/dump_$DATE.rdb $BACKUP_DIR/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

---

## 🔧 Troubleshooting

### Common Issues

1. **SSL Certificate Errors**
   ```bash
   # Check certificate validity
   openssl x509 -in ssl/fullchain.pem -text -noout
   
   # Verify certificate chain
   openssl verify ssl/fullchain.pem
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   docker exec ai-erp-backend-prod python -c "
   from sqlalchemy import create_engine
   engine = create_engine('postgresql://ai_erp_user:PASSWORD@postgres:5432/ai_erp_production')
   engine.connect()
   print('Database connection successful')
   "
   ```

3. **Performance Issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Analyze slow queries
   docker exec ai-erp-postgres-prod psql -U ai_erp_user ai_erp_production -c "
   SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   "
   ```

---

## 📋 Maintenance Tasks

### Daily
- [ ] Check application logs for errors
- [ ] Verify all services are running
- [ ] Monitor resource usage

### Weekly
- [ ] Review security logs
- [ ] Update dependencies
- [ ] Check SSL certificate expiration

### Monthly
- [ ] Security audit
- [ ] Performance review
- [ ] Backup restoration test

---

## 🆘 Emergency Procedures

### 1. **Service Recovery**
```bash
# Restart all services
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart backend
```

### 2. **Database Recovery**
```bash
# Restore from backup
docker exec -i ai-erp-postgres-prod psql -U ai_erp_user ai_erp_production < backup.sql
```

### 3. **Rollback Procedure**
```bash
# Rollback to previous version
git checkout previous-stable-tag
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

---

## 📞 Support Contacts

- **Technical Issues**: [Your DevOps Team]
- **Security Incidents**: [Your Security Team]
- **Database Issues**: [Your DBA Team]
- **Monitoring**: [Your Monitoring Team]

---

**⚠️ REMEMBER: Never deploy to production without completing the security checklist above!**