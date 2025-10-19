#!/bin/bash
# VGM Website Production Deployment Script
# Usage: ./deploy.sh [environment] [version]

set -e

# Configuration
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
APP_NAME="vgm-website"
BACKEND_DIR="/opt/vgm-website"
FRONTEND_DIR="/opt/vgm-website/frontend"
NGINX_CONFIG="/etc/nginx/sites-available/vgm-website"
SYSTEMD_SERVICE="vgm-website"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root or with sudo
check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check if required packages are installed
    local packages=("python3" "python3-pip" "nodejs" "npm" "nginx" "postgresql" "redis-server")
    for package in "${packages[@]}"; do
        if ! command -v "$package" &> /dev/null; then
            error "Required package $package is not installed"
            exit 1
        fi
    done
    
    # Check Python version
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
        error "Python 3.8+ is required, found $python_version"
        exit 1
    fi
    
    # Check Node.js version
    node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $node_version -lt 18 ]]; then
        error "Node.js 18+ is required, found v$node_version"
        exit 1
    fi
    
    log "System requirements check passed"
}

# Setup application directory
setup_directories() {
    log "Setting up application directories..."
    
    # Create application directory
    mkdir -p "$BACKEND_DIR"
    mkdir -p "$BACKEND_DIR/logs"
    mkdir -p "$BACKEND_DIR/uploads"
    mkdir -p "$BACKEND_DIR/backups"
    
    # Set proper permissions
    chown -R www-data:www-data "$BACKEND_DIR"
    chmod -R 755 "$BACKEND_DIR"
    chmod -R 777 "$BACKEND_DIR/logs"
    chmod -R 777 "$BACKEND_DIR/uploads"
    
    log "Application directories created"
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python virtual environment..."
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d ".venv" ]]; then
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    log "Python environment setup complete"
}

# Setup frontend
setup_frontend() {
    log "Setting up frontend..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    npm ci --production
    
    # Build frontend
    npm run build
    
    log "Frontend setup complete"
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    cd "$BACKEND_DIR"
    source .venv/bin/activate
    
    # Run database migrations
    alembic upgrade head
    
    # Create initial data if needed
    if [[ ! -f "data_initialized.flag" ]]; then
        log "Creating initial database data..."
        python -c "
from app_new import create_app
from models_new import db, User, Mosque
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Create admin user if it doesn't exist
    admin_user = User.query.filter_by(email='admin@vgm-gent.be').first()
    if not admin_user:
        admin_user = User(
            email='admin@vgm-gent.be',
            first_name='Admin',
            last_name='User',
            role='BEHEERDER',
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created')
    
    # Create sample mosque if none exist
    if Mosque.query.count() == 0:
        sample_mosque = Mosque(
            name='VGM Gent Centrum',
            address='Gent Centrum',
            phone='+32 9 123 45 67',
            email='info@vgm-gent.be',
            capacity=200,
            established_year=2020,
            imam_name='Imam Ahmed',
            description='Hoofdmoskee van VGM Gent',
            latitude=51.0543,
            longitude=3.7174,
            is_active=True
        )
        db.session.add(sample_mosque)
        db.session.commit()
        print('Sample mosque created')
"
        touch data_initialized.flag
    fi
    
    log "Database setup complete"
}

# Setup systemd service
setup_systemd_service() {
    log "Setting up systemd service..."
    
    cat > "/etc/systemd/system/$SYSTEMD_SERVICE.service" << EOF
[Unit]
Description=VGM Website Backend
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/.venv/bin
ExecStart=$BACKEND_DIR/.venv/bin/python app_new.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$BACKEND_DIR/logs $BACKEND_DIR/uploads $BACKEND_DIR/backups

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vgm-website

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SYSTEMD_SERVICE"
    
    log "Systemd service configured"
}

# Setup Nginx configuration
setup_nginx() {
    log "Setting up Nginx configuration..."
    
    cat > "$NGINX_CONFIG" << EOF
server {
    listen 80;
    server_name vgm-gent.be www.vgm-gent.be;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vgm-gent.be www.vgm-gent.be;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/vgm-gent.be/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vgm-gent.be/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health checks
    location /health {
        proxy_pass http://localhost:5001;
        access_log off;
    }
    
    # Static files
    location /static/ {
        alias $FRONTEND_DIR/.next/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploads
    location /uploads/ {
        alias $BACKEND_DIR/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # File size limits
    client_max_body_size 16M;
}
EOF

    # Enable site and test configuration
    ln -sf "$NGINX_CONFIG" "/etc/nginx/sites-enabled/"
    nginx -t
    
    log "Nginx configuration complete"
}

# Setup SSL certificate
setup_ssl() {
    log "Setting up SSL certificate..."
    
    # Install certbot if not already installed
    if ! command -v certbot &> /dev/null; then
        apt update
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Get SSL certificate
    certbot --nginx -d vgm-gent.be -d www.vgm-gent.be --non-interactive --agree-tos --email admin@vgm-gent.be
    
    # Setup auto-renewal
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    log "SSL certificate setup complete"
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create log rotation configuration
    cat > "/etc/logrotate.d/vgm-website" << EOF
$BACKEND_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload $SYSTEMD_SERVICE
    endscript
}
EOF

    # Setup health check monitoring
    cat > "/usr/local/bin/vgm-health-check.sh" << EOF
#!/bin/bash
# Health check script for VGM Website

HEALTH_URL="http://localhost:5001/health"
RESPONSE=\$(curl -s -o /dev/null -w "%{http_code}" \$HEALTH_URL)

if [[ \$RESPONSE -eq 200 ]]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed with status: \$RESPONSE"
    exit 1
fi
EOF

    chmod +x "/usr/local/bin/vgm-health-check.sh"
    
    # Add health check to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/vgm-health-check.sh") | crontab -
    
    log "Monitoring setup complete"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start backend service
    systemctl start "$SYSTEMD_SERVICE"
    systemctl status "$SYSTEMD_SERVICE" --no-pager
    
    # Start frontend (PM2 recommended for production)
    if command -v pm2 &> /dev/null; then
        cd "$FRONTEND_DIR"
        pm2 start npm --name "vgm-frontend" -- start
        pm2 save
        pm2 startup
    else
        warning "PM2 not installed. Consider installing PM2 for frontend process management."
    fi
    
    # Restart Nginx
    systemctl restart nginx
    systemctl status nginx --no-pager
    
    log "Services started successfully"
}

# Run tests
run_tests() {
    log "Running production tests..."
    
    cd "$BACKEND_DIR"
    source .venv/bin/activate
    
    # Run backend tests
    python -m pytest tests/ --cov=. --cov-report=term-missing
    
    # Test API endpoints
    log "Testing API endpoints..."
    
    # Test health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health)
    if [[ $response -eq 200 ]]; then
        log "Health endpoint test passed"
    else
        error "Health endpoint test failed"
        exit 1
    fi
    
    # Test mosques endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/mosques)
    if [[ $response -eq 200 ]]; then
        log "Mosques endpoint test passed"
    else
        error "Mosques endpoint test failed"
        exit 1
    fi
    
    log "All tests passed"
}

# Main deployment function
deploy() {
    log "Starting VGM Website deployment..."
    log "Environment: $ENVIRONMENT"
    log "Version: $VERSION"
    
    check_permissions
    check_requirements
    setup_directories
    setup_python_env
    setup_frontend
    setup_database
    setup_systemd_service
    setup_nginx
    setup_ssl
    setup_monitoring
    start_services
    run_tests
    
    log "Deployment completed successfully!"
    log "Website should be available at: https://vgm-gent.be"
    log "Health check: https://vgm-gent.be/health"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Stop services
    systemctl stop "$SYSTEMD_SERVICE"
    systemctl stop nginx
    
    # Restore previous version (if backup exists)
    if [[ -d "$BACKEND_DIR.backup" ]]; then
        rm -rf "$BACKEND_DIR"
        mv "$BACKEND_DIR.backup" "$BACKEND_DIR"
        log "Rollback completed"
    else
        error "No backup found for rollback"
        exit 1
    fi
}

# Main script logic
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    test)
        run_tests
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|test}"
        exit 1
        ;;
esac
