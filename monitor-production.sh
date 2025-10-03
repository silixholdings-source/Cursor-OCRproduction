#!/bin/bash

# AI ERP SaaS Production Monitoring Script
# This script monitors the health and performance of the production application

set -e

echo "📊 AI ERP SaaS Production Monitoring..."

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

print_metric() {
    echo -e "${BLUE}[METRIC]${NC} $1"
}

# Configuration
API_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"
LOG_FILE="/var/log/ai-erp-saas/monitoring.log"
ALERT_EMAIL="admin@your-domain.com"

# Create log directory
mkdir -p /var/log/ai-erp-saas

# Function to log metrics
log_metric() {
    local metric="$1"
    local value="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $metric: $value" >> "$LOG_FILE"
}

# Function to send alert
send_alert() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ALERT: $message" >> "$LOG_FILE"
    
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "AI ERP SaaS Production Alert" "$ALERT_EMAIL"
    fi
}

# Check API health
check_api_health() {
    print_status "Checking API health..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" || echo "000")
    
    if [ "$response" = "200" ]; then
        print_metric "API Health: OK"
        log_metric "api_health" "ok"
    else
        print_error "API Health: FAILED (HTTP $response)"
        log_metric "api_health" "failed"
        send_alert "API health check failed with HTTP $response"
    fi
}

# Check detailed API health
check_detailed_api_health() {
    print_status "Checking detailed API health..."
    
    local response=$(curl -s "$API_URL/health/detailed" 2>/dev/null || echo '{"status":"error"}')
    local status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "error")
    
    if [ "$status" = "healthy" ]; then
        print_metric "Detailed API Health: OK"
        log_metric "detailed_api_health" "ok"
    else
        print_error "Detailed API Health: FAILED"
        print_error "Response: $response"
        log_metric "detailed_api_health" "failed"
        send_alert "Detailed API health check failed: $response"
    fi
}

# Check frontend health
check_frontend_health() {
    print_status "Checking frontend health..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" || echo "000")
    
    if [ "$response" = "200" ]; then
        print_metric "Frontend Health: OK"
        log_metric "frontend_health" "ok"
    else
        print_error "Frontend Health: FAILED (HTTP $response)"
        log_metric "frontend_health" "failed"
        send_alert "Frontend health check failed with HTTP $response"
    fi
}

# Check database connectivity
check_database_health() {
    print_status "Checking database health..."
    
    local response=$(curl -s "$API_URL/health/detailed" 2>/dev/null || echo '{"database":{"status":"error"}}')
    local db_status=$(echo "$response" | jq -r '.database.status' 2>/dev/null || echo "error")
    
    if [ "$db_status" = "healthy" ]; then
        print_metric "Database Health: OK"
        log_metric "database_health" "ok"
    else
        print_error "Database Health: FAILED"
        log_metric "database_health" "failed"
        send_alert "Database health check failed: $db_status"
    fi
}

# Check Redis connectivity
check_redis_health() {
    print_status "Checking Redis health..."
    
    local response=$(curl -s "$API_URL/health/detailed" 2>/dev/null || echo '{"redis":{"status":"error"}}')
    local redis_status=$(echo "$response" | jq -r '.redis.status' 2>/dev/null || echo "error")
    
    if [ "$redis_status" = "healthy" ]; then
        print_metric "Redis Health: OK"
        log_metric "redis_health" "ok"
    else
        print_error "Redis Health: FAILED"
        log_metric "redis_health" "failed"
        send_alert "Redis health check failed: $redis_status"
    fi
}

# Check system resources
check_system_resources() {
    print_status "Checking system resources..."
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    print_metric "CPU Usage: ${cpu_usage}%"
    log_metric "cpu_usage" "$cpu_usage"
    
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        send_alert "High CPU usage: ${cpu_usage}%"
    fi
    
    # Memory usage
    local memory_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    print_metric "Memory Usage: ${memory_usage}%"
    log_metric "memory_usage" "$memory_usage"
    
    if (( $(echo "$memory_usage > 80" | bc -l) )); then
        send_alert "High memory usage: ${memory_usage}%"
    fi
    
    # Disk usage
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    print_metric "Disk Usage: ${disk_usage}%"
    log_metric "disk_usage" "$disk_usage"
    
    if [ "$disk_usage" -gt 80 ]; then
        send_alert "High disk usage: ${disk_usage}%"
    fi
}

# Check Docker containers
check_docker_containers() {
    print_status "Checking Docker containers..."
    
    local containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(ai-erp|postgres|redis|nginx)")
    
    if [ -n "$containers" ]; then
        print_metric "Docker Containers:"
        echo "$containers"
        log_metric "docker_containers" "running"
    else
        print_error "No AI ERP containers found"
        log_metric "docker_containers" "not_found"
        send_alert "No AI ERP containers found running"
    fi
}

# Check application logs for errors
check_application_logs() {
    print_status "Checking application logs for errors..."
    
    local error_count=$(docker logs ai-erp-backend 2>&1 | grep -i error | wc -l)
    local warning_count=$(docker logs ai-erp-backend 2>&1 | grep -i warning | wc -l)
    
    print_metric "Backend Errors: $error_count"
    print_metric "Backend Warnings: $warning_count"
    log_metric "backend_errors" "$error_count"
    log_metric "backend_warnings" "$warning_count"
    
    if [ "$error_count" -gt 10 ]; then
        send_alert "High number of backend errors: $error_count"
    fi
}

# Check API response times
check_api_performance() {
    print_status "Checking API performance..."
    
    local start_time=$(date +%s%N)
    curl -s "$API_URL/health" > /dev/null
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    print_metric "API Response Time: ${response_time}ms"
    log_metric "api_response_time" "$response_time"
    
    if [ "$response_time" -gt 1000 ]; then
        send_alert "Slow API response time: ${response_time}ms"
    fi
}

# Check SSL certificate expiry
check_ssl_certificate() {
    print_status "Checking SSL certificate..."
    
    local domain="your-domain.com"  # Update with your actual domain
    local expiry_date=$(echo | openssl s_client -servername "$domain" -connect "$domain":443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    
    if [ -n "$expiry_date" ]; then
        local expiry_timestamp=$(date -d "$expiry_date" +%s)
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        print_metric "SSL Certificate Expires: $expiry_date ($days_until_expiry days)"
        log_metric "ssl_days_until_expiry" "$days_until_expiry"
        
        if [ "$days_until_expiry" -lt 30 ]; then
            send_alert "SSL certificate expires in $days_until_expiry days"
        fi
    else
        print_warning "Could not check SSL certificate (may not be configured)"
    fi
}

# Generate monitoring report
generate_report() {
    print_status "Generating monitoring report..."
    
    local report_file="/var/log/ai-erp-saas/monitoring-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "AI ERP SaaS Production Monitoring Report"
        echo "Generated: $(date)"
        echo "========================================"
        echo
        echo "System Resources:"
        echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
        echo "Memory Usage: $(free | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
        echo "Disk Usage: $(df / | awk 'NR==2 {print $5}')"
        echo
        echo "Application Status:"
        echo "API Health: $(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health")"
        echo "Frontend Health: $(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")"
        echo
        echo "Docker Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo
        echo "Recent Logs:"
        tail -n 20 "$LOG_FILE"
    } > "$report_file"
    
    print_status "Monitoring report generated: $report_file"
}

# Main monitoring function
main() {
    print_status "Starting AI ERP SaaS Production Monitoring..."
    
    check_api_health
    check_detailed_api_health
    check_frontend_health
    check_database_health
    check_redis_health
    check_system_resources
    check_docker_containers
    check_application_logs
    check_api_performance
    check_ssl_certificate
    generate_report
    
    print_status "🎉 Monitoring completed!"
    print_status "Logs available at: $LOG_FILE"
}

# Run main function
main "$@"

