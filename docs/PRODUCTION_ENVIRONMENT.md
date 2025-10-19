# Production Environment Configuration for VGM Website

## Environment Variables

### Database Configuration
```bash
# PostgreSQL Production Database
DATABASE_URL=postgresql://vgm_user:${DB_PASSWORD}@${DB_HOST}:5432/vgm_database
SQLALCHEMY_DATABASE_URI=${DATABASE_URL}
DB_HOST=your-postgres-host.com
DB_PASSWORD=your-secure-password
DB_NAME=vgm_database
DB_USER=vgm_user
```

### Redis Configuration
```bash
# Redis for caching and sessions
REDIS_URL=redis://${REDIS_HOST}:6379/0
REDIS_HOST=your-redis-host.com
REDIS_PASSWORD=your-redis-password
```

### Security Configuration
```bash
# JWT and Security
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
WTF_CSRF_ENABLED=true
RATELIMIT_DEFAULT=200 per day, 50 per hour
```

### Stripe Configuration
```bash
# Payment Processing
STRIPE_SECRET_KEY=sk_live_your_live_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### Monitoring & Error Tracking
```bash
# Sentry Error Tracking
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

### Email Configuration
```bash
# Email Service (for notifications)
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@vgm-gent.be
MAIL_PASSWORD=your-email-password
```

### File Storage
```bash
# File Upload Configuration
UPLOAD_FOLDER=/var/www/vgm-website/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx
```

### Application Configuration
```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO
```

## Production Server Requirements

### Minimum Server Specifications
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04 LTS or newer

### Recommended Server Specifications
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **OS**: Ubuntu 22.04 LTS

### Required Services
- PostgreSQL 14+
- Redis 6+
- Nginx (reverse proxy)
- SSL Certificate (Let's Encrypt)
- Backup storage (S3 or local)

## Security Checklist

### SSL/TLS Configuration
- [ ] SSL certificate installed and configured
- [ ] HTTPS redirect enabled
- [ ] HSTS headers configured
- [ ] Security headers (CSP, X-Frame-Options, etc.)

### Database Security
- [ ] PostgreSQL configured with SSL
- [ ] Database user has minimal required permissions
- [ ] Database backups encrypted
- [ ] Connection pooling configured

### Application Security
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] File upload restrictions
- [ ] JWT tokens properly configured

### Infrastructure Security
- [ ] Firewall configured (only necessary ports open)
- [ ] SSH key-based authentication
- [ ] Regular security updates enabled
- [ ] Log monitoring configured
- [ ] Intrusion detection system (optional)

## Performance Optimization

### Database Optimization
- [ ] Connection pooling configured
- [ ] Database indexes optimized
- [ ] Query performance monitored
- [ ] Regular VACUUM and ANALYZE scheduled

### Caching Strategy
- [ ] Redis caching enabled
- [ ] CDN configured for static assets
- [ ] Browser caching headers set
- [ ] API response caching implemented

### Application Optimization
- [ ] Gzip compression enabled
- [ ] Static file serving optimized
- [ ] Database query optimization
- [ ] Memory usage monitoring

## Monitoring & Alerting

### Health Checks
- [ ] Application health endpoint configured
- [ ] Database connectivity monitoring
- [ ] Redis connectivity monitoring
- [ ] External service monitoring (Stripe)

### Logging
- [ ] Structured logging configured
- [ ] Log rotation configured
- [ ] Error log monitoring
- [ ] Access log analysis

### Alerting
- [ ] Server resource monitoring
- [ ] Application error alerting
- [ ] Database performance alerting
- [ ] SSL certificate expiration alerts

## Backup Strategy

### Database Backups
- [ ] Daily automated backups
- [ ] Backup retention policy (30 days)
- [ ] Backup verification process
- [ ] Disaster recovery testing

### File Backups
- [ ] Upload files backup strategy
- [ ] Configuration files backup
- [ ] Application code backup (Git)

### Recovery Procedures
- [ ] Database restore procedures documented
- [ ] Application rollback procedures
- [ ] Disaster recovery runbook
- [ ] Recovery time objectives defined
