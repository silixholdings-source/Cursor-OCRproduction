# AI ERP SaaS Application - Production Readiness Guide

This document outlines the steps taken to make the AI ERP SaaS application production-ready and provides guidelines for deployment, monitoring, backup, and maintenance.

## Table of Contents

1. [Issues Fixed](#issues-fixed)
2. [Application Architecture](#application-architecture)
3. [Deployment Instructions](#deployment-instructions)
4. [Monitoring Setup](#monitoring-setup)
5. [Backup and Restore Procedures](#backup-and-restore-procedures)
6. [Security Considerations](#security-considerations)
7. [Performance Optimizations](#performance-optimizations)
8. [Maintenance Guidelines](#maintenance-guidelines)

## Issues Fixed

The following issues were identified and fixed during the production readiness review:

1. **Next.js Client/Server Component Issues**:
   - Fixed "Event handlers cannot be passed to Client Component props" error by creating a dedicated client-side button wrapper.
   - Created `web/src/components/ui/client-button.tsx` to handle client-side interactivity.

2. **Docker Configuration Issues**:
   - Updated Docker Compose files for development and production environments.
   - Fixed container health checks for reliable monitoring.
   - Optimized resource limits and reservations for better performance.

3. **Environment Setup**:
   - Created scripts to automate environment variable setup.
   - Fixed duplicate dependencies in requirements.txt.

4. **Next.js Metadata Issues**:
   - Fixed `metadataBase` warning in `web/src/app/layout.tsx`.
   - Removed `'use client'` directive from layout file to allow metadata export.
   - Enhanced social sharing metadata configuration.

5. **Backend Health Check Issues**:
   - Implemented a Python-based health check script for the backend container.
   - Configured appropriate health check parameters for container orchestration.

## Application Architecture

The AI ERP SaaS application consists of the following components:

- **PostgreSQL Database**: Stores application data
- **Redis Cache**: Provides caching and session management
- **Backend API (FastAPI)**: Handles business logic and API endpoints
- **Web Frontend (Next.js)**: Provides the user interface
- **Nginx Reverse Proxy**: Routes traffic and handles SSL termination
- **Monitoring Stack**: Prometheus, AlertManager, Grafana for observability

## Deployment Instructions

### Prerequisites

- Docker and Docker Compose installed
- SSL certificates (for production)
- Environment variables configured

### Development Deployment

1. Set up environment variables:
   ```powershell
   # Windows
   .\setup-env.ps1
   ```
   ```bash
   # Linux/macOS
   ./setup-env.sh
   ```

2. Start the backend services:
   ```bash
   docker-compose -f docker-compose.backend.yml up -d
   ```

3. Start the web frontend:
   ```bash
   docker-compose -f docker-compose.web.yml up -d
   ```

4. Start the monitoring stack:
   ```bash
   docker-compose -f monitoring/docker-compose.monitoring.yml up -d
   ```

### Production Deployment

1. Set up environment variables:
   ```bash
   cp env.example .env
   cp web/env.example web/.env
   # Edit .env files with production values
   ```

2. Start all services:
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

3. Verify deployment:
   ```bash
   docker ps
   curl http://localhost/health
   ```

## Monitoring Setup

The monitoring stack includes:

- **Prometheus**: Metrics collection and storage
- **AlertManager**: Alert routing and notifications
- **Grafana**: Visualization and dashboards
- **Node Exporter**: Host metrics
- **cAdvisor**: Container metrics
- **Postgres Exporter**: Database metrics
- **Redis Exporter**: Cache metrics

Access the monitoring interfaces:
- Prometheus: http://localhost:9090
- AlertManager: http://localhost:9093
- Grafana: http://localhost:3001 (default credentials: admin/admin)

## Backup and Restore Procedures

### Backup

Run the backup script to create a complete backup of the application:

```powershell
# Windows
.\scripts\backup.ps1
```

```bash
# Linux/macOS
./scripts/backup.sh
```

The backup includes:
- PostgreSQL database dump
- Redis data snapshot
- Application files (backend/src, backend/models, backend/uploads, web/src)

Backups are stored in the `backups` directory with timestamps.

### Restore

To restore from a backup:

```powershell
# Windows
.\scripts\restore.ps1 .\backups\ai-erp-saas_backup_20250916_123456.zip
```

```bash
# Linux/macOS
./scripts/restore.sh ./backups/ai-erp-saas_backup_20250916_123456.tar.gz
```

## Security Considerations

1. **Network Security**:
   - All services in production bind only to localhost (127.0.0.1)
   - Only Nginx exposes ports 80 and 443 to the public
   - Use a firewall to restrict access to necessary ports

2. **Container Security**:
   - Resource limits prevent DoS attacks
   - Read-only volumes where possible
   - Non-root users in containers

3. **Application Security**:
   - CORS restrictions
   - Rate limiting
   - Security headers (CSP, X-Frame-Options, etc.)
   - Input validation

## Performance Optimizations

1. **Database Optimizations**:
   - Connection pooling
   - Query optimization
   - Proper indexing

2. **Redis Cache**:
   - Memory limits (1GB)
   - LRU eviction policy

3. **Backend API**:
   - Multiple workers (4)
   - CPU and memory limits
   - Gzip compression

4. **Web Frontend**:
   - Server-side rendering where appropriate
   - Client components for interactivity
   - Image optimization

5. **Nginx**:
   - Response caching
   - Gzip compression
   - Connection limits

## Maintenance Guidelines

1. **Regular Updates**:
   - Update dependencies monthly
   - Apply security patches promptly
   - Test updates in development before deploying to production

2. **Database Maintenance**:
   - Run VACUUM ANALYZE weekly
   - Monitor table sizes and growth
   - Implement data retention policies

3. **Monitoring and Alerting**:
   - Review alerts daily
   - Adjust thresholds as needed
   - Add new metrics for emerging patterns

4. **Backup Verification**:
   - Test restore procedures quarterly
   - Verify backup integrity
   - Store backups off-site

5. **Performance Testing**:
   - Run load tests before major releases
   - Monitor response times
   - Identify bottlenecks

By following these guidelines, the AI ERP SaaS application will maintain high availability, security, and performance in production.