#!/bin/bash

# AI ERP SaaS Production Deployment Script
# This script deploys the AI ERP SaaS application to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if production environment file exists
if [ ! -f "env.production" ]; then
    print_error "Production environment file not found. Please create env.production file."
    exit 1
fi

# Check if SSL certificates exist
if [ ! -d "ssl" ]; then
    print_warning "SSL directory not found. Creating directory for SSL certificates."
    mkdir -p ssl
    print_warning "Please place your SSL certificates in the ssl directory:"
    print_warning "  - ssl/cert.pem"
    print_warning "  - ssl/key.pem"
fi

# Backup current deployment
backup_current_deployment() {
    print_status "Backing up current deployment..."
    
    # Create backup directory
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup environment files
    cp env.production "$BACKUP_DIR/"
    
    # Backup database (if PostgreSQL is running)
    if docker ps | grep -q postgres; then
        print_status "Backing up database..."
        docker exec -t ai-erp-postgres pg_dumpall -c -U ai_erp_user > "$BACKUP_DIR/database_backup.sql"
    else
        print_warning "PostgreSQL container not running. Skipping database backup."
    fi
    
    print_status "Backup completed: $BACKUP_DIR"
}

# Pull latest code
pull_latest_code() {
    print_status "Pulling latest code..."
    
    # If using git
    if [ -d ".git" ]; then
        git pull origin main
    else
        print_warning "Not a git repository. Skipping code pull."
    fi
}

# Build Docker images
build_docker_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    docker build -t ai-erp-backend:latest ./backend
    
    # Build frontend image
    docker build -t ai-erp-frontend:latest ./web
    
    print_status "Docker images built successfully."
}

# Run database migrations
run_database_migrations() {
    print_status "Running database migrations..."
    
    # Check if database is running
    if ! docker ps | grep -q postgres; then
        print_warning "PostgreSQL container not running. Starting database container..."
        docker-compose -f docker-compose.production.yml up -d postgres
        sleep 10 # Wait for database to start
    fi
    
    # Run migrations
    docker-compose -f docker-compose.production.yml run --rm backend alembic upgrade head
    
    print_status "Database migrations completed."
}

# Deploy application
deploy_application() {
    print_status "Deploying application..."
    
    # Stop existing containers
    docker-compose -f docker-compose.production.yml down
    
    # Start new containers
    docker-compose -f docker-compose.production.yml up -d
    
    print_status "Application deployed."
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Wait for services to start
    sleep 10
    
    # Check if containers are running
    if ! docker ps | grep -q ai-erp-backend; then
        print_error "Backend container not running!"
        exit 1
    fi
    
    if ! docker ps | grep -q ai-erp-frontend; then
        print_error "Frontend container not running!"
        exit 1
    fi
    
    if ! docker ps | grep -q ai-erp-nginx; then
        print_error "Nginx container not running!"
        exit 1
    fi
    
    # Check health endpoints
    if ! curl -s http://localhost/health > /dev/null; then
        print_error "Health check failed!"
        exit 1
    fi
    
    print_status "Deployment verification successful."
}

# Run post-deployment tasks
run_post_deployment_tasks() {
    print_status "Running post-deployment tasks..."
    
    # Clear cache
    docker-compose -f docker-compose.production.yml exec redis redis-cli FLUSHALL
    
    # Warm up cache (optional)
    # Add your cache warming logic here
    
    print_status "Post-deployment tasks completed."
}

# Main deployment function
main() {
    print_status "Starting AI ERP SaaS Production Deployment..."
    
    # Confirm deployment
    read -p "Are you sure you want to deploy to production? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled."
        exit 0
    fi
    
    # Run deployment steps
    backup_current_deployment
    pull_latest_code
    build_docker_images
    run_database_migrations
    deploy_application
    verify_deployment
    run_post_deployment_tasks
    
    print_status "🎉 Production deployment completed successfully!"
    print_status ""
    print_warning "⚠️  IMPORTANT DEPLOYMENT NOTES:"
    print_warning "1. Monitor application logs: docker-compose -f docker-compose.production.yml logs -f"
    print_warning "2. Check application health: curl http://localhost/health"
    print_warning "3. Verify all features are working correctly"
    print_warning "4. Monitor system resources"
    print_warning "5. Update DNS records if needed"
}

# Run main function
main "$@"































