#!/bin/bash

# AI ERP SaaS Production Security Hardening Script
# This script applies security best practices to the production environment

set -e

echo "🔒 Hardening AI ERP SaaS Production Environment..."

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system packages
update_system() {
    print_status "Updating system packages..."
    apt-get update
    apt-get upgrade -y
    print_status "System packages updated."
}

# Install security tools
install_security_tools() {
    print_status "Installing security tools..."
    apt-get install -y \
        fail2ban \
        ufw \
        unattended-upgrades \
        apt-listchanges \
        rkhunter \
        chkrootkit \
        lynis
    print_status "Security tools installed."
}

# Configure firewall
configure_firewall() {
    print_status "Configuring firewall..."
    
    # Reset UFW
    ufw --force reset
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (be careful with this)
    ufw allow ssh
    
    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow Docker daemon (if needed)
    ufw allow 2376/tcp
    
    # Enable firewall
    ufw --force enable
    
    print_status "Firewall configured."
}

# Configure fail2ban
configure_fail2ban() {
    print_status "Configuring fail2ban..."
    
    # Create jail.local
    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
EOF

    # Create nginx-http-auth filter
    cat > /etc/fail2ban/filter.d/nginx-http-auth.conf << EOF
[Definition]
failregex = ^<HOST> -.*"(GET|POST).*HTTP.*" (401|403) .*$
ignoreregex =
EOF

    # Create nginx-limit-req filter
    cat > /etc/fail2ban/filter.d/nginx-limit-req.conf << EOF
[Definition]
failregex = limiting requests, excess: .* by zone .*, client: <HOST>
ignoreregex =
EOF

    # Restart fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    print_status "Fail2ban configured."
}

# Configure automatic security updates
configure_auto_updates() {
    print_status "Configuring automatic security updates..."
    
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};

Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

    # Enable automatic updates
    echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades
    echo 'Unattended-Upgrade::Automatic-Reboot-Time "02:00";' >> /etc/apt/apt.conf.d/50unattended-upgrades
    
    systemctl enable unattended-upgrades
    systemctl start unattended-upgrades
    
    print_status "Automatic security updates configured."
}

# Configure Docker security
configure_docker_security() {
    print_status "Configuring Docker security..."
    
    # Create Docker daemon configuration
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "live-restore": true,
    "userland-proxy": false,
    "no-new-privileges": true
}
EOF

    # Restart Docker
    systemctl restart docker
    
    print_status "Docker security configured."
}

# Configure log rotation
configure_log_rotation() {
    print_status "Configuring log rotation..."
    
    cat > /etc/logrotate.d/ai-erp-saas << EOF
/var/log/ai-erp-saas/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        /bin/kill -USR1 \`cat /var/run/nginx.pid 2> /dev/null\` 2> /dev/null || true
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        /bin/kill -USR1 \`cat /var/run/nginx.pid 2> /dev/null\` 2> /dev/null || true
    endscript
}
EOF

    print_status "Log rotation configured."
}

# Configure system limits
configure_system_limits() {
    print_status "Configuring system limits..."
    
    cat >> /etc/security/limits.conf << EOF
# AI ERP SaaS limits
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
EOF

    cat >> /etc/sysctl.conf << EOF
# AI ERP SaaS kernel parameters
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535
vm.swappiness = 10
EOF

    sysctl -p
    
    print_status "System limits configured."
}

# Create security monitoring script
create_security_monitoring() {
    print_status "Creating security monitoring script..."
    
    cat > /usr/local/bin/security-monitor.sh << 'EOF'
#!/bin/bash

# AI ERP SaaS Security Monitoring Script
# This script monitors security events and sends alerts

LOG_FILE="/var/log/ai-erp-saas/security-monitor.log"
ALERT_EMAIL="admin@your-domain.com"

# Create log directory
mkdir -p /var/log/ai-erp-saas

# Function to log and alert
log_and_alert() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$LOG_FILE"
    
    # Send email alert (if mail is configured)
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "AI ERP SaaS Security Alert" "$ALERT_EMAIL"
    fi
}

# Check for failed login attempts
check_failed_logins() {
    local failed_count=$(grep "Failed password" /var/log/auth.log | grep "$(date '+%b %d')" | wc -l)
    if [ "$failed_count" -gt 10 ]; then
        log_and_alert "High number of failed login attempts: $failed_count"
    fi
}

# Check for suspicious processes
check_suspicious_processes() {
    local suspicious=$(ps aux | grep -E "(nc|netcat|nmap|masscan)" | grep -v grep)
    if [ -n "$suspicious" ]; then
        log_and_alert "Suspicious processes detected: $suspicious"
    fi
}

# Check disk usage
check_disk_usage() {
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -gt 80 ]; then
        log_and_alert "High disk usage: ${usage}%"
    fi
}

# Check memory usage
check_memory_usage() {
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$usage" -gt 90 ]; then
        log_and_alert "High memory usage: ${usage}%"
    fi
}

# Run all checks
check_failed_logins
check_suspicious_processes
check_disk_usage
check_memory_usage
EOF

    chmod +x /usr/local/bin/security-monitor.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/security-monitor.sh") | crontab -
    
    print_status "Security monitoring script created."
}

# Run security scan
run_security_scan() {
    print_status "Running security scan..."
    
    # Run rkhunter
    rkhunter --update
    rkhunter --check --skip-keypress
    
    # Run chkrootkit
    chkrootkit
    
    # Run lynis
    lynis audit system
    
    print_status "Security scan completed."
}

# Main hardening function
main() {
    print_status "Starting AI ERP SaaS Production Security Hardening..."
    
    update_system
    install_security_tools
    configure_firewall
    configure_fail2ban
    configure_auto_updates
    configure_docker_security
    configure_log_rotation
    configure_system_limits
    create_security_monitoring
    run_security_scan
    
    print_status "🎉 Security hardening completed!"
    print_status ""
    print_warning "⚠️  IMPORTANT SECURITY NOTES:"
    print_warning "1. Review firewall rules: ufw status"
    print_warning "2. Check fail2ban status: fail2ban-client status"
    print_warning "3. Monitor security logs: tail -f /var/log/ai-erp-saas/security-monitor.log"
    print_warning "4. Regularly update system packages"
    print_warning "5. Monitor for security alerts"
    print_warning "6. Consider setting up intrusion detection system (IDS)"
    print_warning "7. Implement regular security audits"
    print_warning "8. Keep SSL certificates updated"
    print_warning "9. Monitor application logs for suspicious activity"
    print_warning "10. Implement backup and disaster recovery procedures"
}

# Run main function
main "$@"

