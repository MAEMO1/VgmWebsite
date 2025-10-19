# VGM Website - Production Deployment Guide

## Quick Start Deployment

### Prerequisites
- Ubuntu 22.04 LTS server
- Domain name pointing to server
- SSH access to server
- Basic knowledge of Linux administration

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx postgresql postgresql-contrib redis-server certbot python3-certbot-nginx

# Install PM2 for process management
sudo npm install -g pm2
```

### 2. Database Setup
```bash
# Create database and user
sudo -u postgres createuser vgm_user
sudo -u postgres createdb vgm_database
sudo -u postgres psql -c "ALTER USER vgm_user PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vgm_database TO vgm_user;"
```

### 3. Application Deployment
```bash
# Clone repository
sudo git clone https://github.com/your-org/vgm-website.git /opt/vgm-website
cd /opt/vgm-website

# Make deployment script executable
sudo chmod +x scripts/deploy.sh

# Run deployment
sudo ./scripts/deploy.sh production latest
```

### 4. SSL Certificate
```bash
# Get SSL certificate
sudo certbot --nginx -d vgm-gent.be -d www.vgm-gent.be --non-interactive --agree-tos --email admin@vgm-gent.be
```

### 5. Verify Deployment
```bash
# Run production tests
sudo ./scripts/production-test.sh all
```

## Detailed Deployment Steps

### Environment Configuration

#### 1. Create Environment File
```bash
# Create production environment file
sudo nano /opt/vgm-website/.env.production
```

Add the following content:
```bash
# Database Configuration
DATABASE_URL=postgresql://vgm_user:your_secure_password@localhost:5432/vgm_database
SQLALCHEMY_DATABASE_URI=${DATABASE_URL}

# Security
SECRET_KEY=your_super_secure_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
WTF_CSRF_ENABLED=true

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_live_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Sentry Configuration
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production

# Email Configuration
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@vgm-gent.be
MAIL_PASSWORD=your-email-password

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO
```

#### 2. Database Migration
```bash
cd /opt/vgm-website
source .venv/bin/activate

# Run database migrations
alembic upgrade head

# Create initial data
python -c "
from app_new import create_app
from models_new import db, User, Mosque
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Create admin user
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
"
```

#### 3. Frontend Build
```bash
cd /opt/vgm-website/frontend

# Install dependencies
npm ci --production

# Build frontend
npm run build
```

#### 4. Service Configuration

Create systemd service:
```bash
sudo nano /etc/systemd/system/vgm-website.service
```

Add the following content:
```ini
[Unit]
Description=VGM Website Backend
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/vgm-website
Environment=PATH=/opt/vgm-website/.venv/bin
ExecStart=/opt/vgm-website/.venv/bin/python app_new.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/vgm-website/logs /opt/vgm-website/uploads /opt/vgm-website/backups

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vgm-website

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vgm-website
sudo systemctl start vgm-website
```

#### 5. Nginx Configuration

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/vgm-website
```

Add the following content:
```nginx
server {
    listen 80;
    server_name vgm-gent.be www.vgm-gent.be;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
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
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health checks
    location /health {
        proxy_pass http://localhost:5001;
        access_log off;
    }
    
    # Static files
    location /static/ {
        alias /opt/vgm-website/frontend/.next/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploads
    location /uploads/ {
        alias /opt/vgm-website/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # File size limits
    client_max_body_size 16M;
}
```

Enable the site:
```bash
sudo ln -sf /etc/nginx/sites-available/vgm-website /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Frontend Process Management

Start frontend with PM2:
```bash
cd /opt/vgm-website/frontend
sudo -u www-data pm2 start npm --name "vgm-frontend" -- start
sudo -u www-data pm2 save
sudo -u www-data pm2 startup
```

## Post-Deployment Verification

### 1. Service Status Check
```bash
# Check backend service
sudo systemctl status vgm-website

# Check frontend service
sudo -u www-data pm2 status

# Check Nginx
sudo systemctl status nginx

# Check database
sudo systemctl status postgresql

# Check Redis
sudo systemctl status redis-server
```

### 2. Health Check
```bash
# Test health endpoints
curl http://localhost:5001/health
curl http://localhost:5001/health/ready
curl http://localhost:5001/health/live

# Test public endpoints
curl https://vgm-gent.be/health
curl https://vgm-gent.be/api/mosques
```

### 3. Run Production Tests
```bash
cd /opt/vgm-website
sudo ./scripts/production-test.sh all
```

## Monitoring Setup

### 1. Log Monitoring
```bash
# View application logs
sudo journalctl -u vgm-website -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View application logs
sudo tail -f /opt/vgm-website/logs/app.log
```

### 2. Health Check Monitoring
```bash
# Create health check script
sudo nano /usr/local/bin/vgm-health-check.sh
```

Add the following content:
```bash
#!/bin/bash
HEALTH_URL="http://localhost:5001/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [[ $RESPONSE -eq 200 ]]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed with status: $RESPONSE"
    exit 1
fi
```

Make it executable:
```bash
sudo chmod +x /usr/local/bin/vgm-health-check.sh
```

Add to crontab:
```bash
sudo crontab -e
# Add: */5 * * * * /usr/local/bin/vgm-health-check.sh
```

### 3. Backup Setup
```bash
# Create backup script
sudo nano /usr/local/bin/vgm-backup.sh
```

Add the following content:
```bash
#!/bin/bash
BACKUP_DIR="/opt/vgm-website/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/vgm_db_backup_$DATE.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create database backup
pg_dump -h localhost -U vgm_user -d vgm_database > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "vgm_db_backup_*.sql.gz" -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

Make it executable:
```bash
sudo chmod +x /usr/local/bin/vgm-backup.sh
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/vgm-backup.sh
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status vgm-website

# Check logs
sudo journalctl -u vgm-website -n 50

# Check configuration
sudo nginx -t
```

#### 2. Database Connection Issues
```bash
# Test database connection
psql -h localhost -U vgm_user -d vgm_database -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 3. Frontend Issues
```bash
# Check PM2 status
sudo -u www-data pm2 status

# Check PM2 logs
sudo -u www-data pm2 logs vgm-frontend

# Restart frontend
sudo -u www-data pm2 restart vgm-frontend
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test SSL
openssl s_client -connect vgm-gent.be:443 -servername vgm-gent.be
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Check service status
- Review error logs
- Monitor disk space
- Check backup status

#### Weekly
- Review performance metrics
- Check SSL certificate expiration
- Update system packages
- Review security logs

#### Monthly
- Test disaster recovery procedures
- Review and update documentation
- Performance optimization review
- Security audit

### Updates and Upgrades

#### Application Updates
```bash
# Pull latest code
cd /opt/vgm-website
sudo git pull origin main

# Update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart vgm-website
sudo -u www-data pm2 restart vgm-frontend
```

#### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services if needed
sudo systemctl restart vgm-website
sudo systemctl restart nginx
```

## Security Considerations

### 1. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw deny 5001  # Block direct access to backend
```

### 2. Regular Security Updates
```bash
# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Monitoring Security Events
```bash
# Monitor failed login attempts
sudo tail -f /var/log/auth.log | grep "Failed password"

# Monitor application security logs
sudo tail -f /opt/vgm-website/logs/app.log | grep "security"
```

---

**Note**: This deployment guide should be customized based on your specific server configuration and requirements. Always test the deployment process in a staging environment before deploying to production.
