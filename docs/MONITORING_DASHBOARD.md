# VGM Website - Monitoring Dashboard Configuration

## Overview
This document outlines the monitoring setup for the VGM Website production environment, including health checks, metrics collection, and alerting configuration.

## Health Check Endpoints

### Application Health Checks
```bash
# Basic health check
curl https://vgm-gent.be/health

# Detailed readiness check
curl https://vgm-gent.be/health/ready

# Liveness check
curl https://vgm-gent.be/health/live
```

### Expected Responses

#### Basic Health Check (`/health`)
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Readiness Check (`/health/ready`)
```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": true,
    "stripe": true,
    "redis": true
  }
}
```

#### Liveness Check (`/health/live`)
```json
{
  "status": "alive",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Monitoring Metrics

### Application Metrics
- **Response Time**: Average API response time
- **Error Rate**: Percentage of failed requests
- **Request Rate**: Requests per minute
- **Active Users**: Concurrent active users
- **Database Connections**: Active database connections

### Infrastructure Metrics
- **CPU Usage**: Server CPU utilization
- **Memory Usage**: RAM utilization
- **Disk Usage**: Disk space utilization
- **Network I/O**: Network traffic
- **Load Average**: System load average

### Database Metrics
- **Connection Pool**: Active/idle connections
- **Query Performance**: Slow query detection
- **Database Size**: Database growth
- **Backup Status**: Last backup timestamp
- **Replication Lag**: If using read replicas

### Cache Metrics
- **Redis Memory**: Redis memory usage
- **Cache Hit Rate**: Cache effectiveness
- **Key Expiration**: Expired keys count
- **Connection Count**: Active Redis connections

## Alerting Configuration

### Critical Alerts (Immediate Response)
- **Service Down**: Application not responding
- **Database Down**: Database connection failed
- **High Error Rate**: Error rate > 5%
- **High Response Time**: Response time > 5 seconds
- **Disk Space**: Disk usage > 90%
- **Memory Usage**: Memory usage > 90%

### Warning Alerts (Monitor Closely)
- **High CPU**: CPU usage > 80%
- **Slow Queries**: Database queries > 1 second
- **Cache Miss Rate**: Cache hit rate < 80%
- **SSL Certificate**: Certificate expires in 30 days
- **Backup Failure**: Daily backup failed

### Info Alerts (Log Only)
- **Deployment**: New deployment completed
- **User Registration**: New user registered
- **Payment Processed**: Successful payment
- **File Upload**: File uploaded successfully

## Monitoring Tools Configuration

### Prometheus Metrics (Optional)
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'vgm-website'
    static_configs:
      - targets: ['localhost:5001']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### Grafana Dashboard (Optional)
```json
{
  "dashboard": {
    "title": "VGM Website Monitoring",
    "panels": [
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(http_request_duration_seconds)",
            "legendFormat": "Average Response Time"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

## Log Monitoring

### Log Levels
- **ERROR**: System errors, exceptions
- **WARNING**: Performance issues, deprecated usage
- **INFO**: General application flow
- **DEBUG**: Detailed debugging information

### Log Patterns to Monitor
```bash
# Error patterns
grep "ERROR" /var/log/vgm-website/app.log
grep "Exception" /var/log/vgm-website/app.log
grep "500" /var/log/vgm-website/access.log

# Performance patterns
grep "slow query" /var/log/vgm-website/app.log
grep "timeout" /var/log/vgm-website/app.log

# Security patterns
grep "unauthorized" /var/log/vgm-website/app.log
grep "rate limit" /var/log/vgm-website/app.log
```

## Automated Monitoring Scripts

### Health Check Script
```bash
#!/bin/bash
# /usr/local/bin/vgm-health-check.sh

HEALTH_URL="http://localhost:5001/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [[ $RESPONSE -eq 200 ]]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed with status: $RESPONSE"
    # Send alert notification
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"VGM Website health check failed: '$RESPONSE'"}' \
        $SLACK_WEBHOOK_URL
    exit 1
fi
```

### Database Monitoring Script
```bash
#!/bin/bash
# /usr/local/bin/vgm-db-check.sh

DB_CONNECTION=$(psql -h localhost -U vgm_user -d vgm_database -c "SELECT 1;" 2>/dev/null)

if [[ $? -eq 0 ]]; then
    echo "Database connection successful"
    exit 0
else
    echo "Database connection failed"
    # Send alert notification
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"VGM Website database connection failed"}' \
        $SLACK_WEBHOOK_URL
    exit 1
fi
```

### Disk Space Monitoring Script
```bash
#!/bin/bash
# /usr/local/bin/vgm-disk-check.sh

DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

if [[ $DISK_USAGE -gt 90 ]]; then
    echo "Disk usage critical: ${DISK_USAGE}%"
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"VGM Website disk usage critical: '$DISK_USAGE'%"}' \
        $SLACK_WEBHOOK_URL
    exit 1
elif [[ $DISK_USAGE -gt 80 ]]; then
    echo "Disk usage warning: ${DISK_USAGE}%"
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"VGM Website disk usage warning: '$DISK_USAGE'%"}' \
        $SLACK_WEBHOOK_URL
fi

exit 0
```

## Cron Jobs for Monitoring

```bash
# Add to crontab
# Health check every 5 minutes
*/5 * * * * /usr/local/bin/vgm-health-check.sh

# Database check every 10 minutes
*/10 * * * * /usr/local/bin/vgm-db-check.sh

# Disk space check every hour
0 * * * * /usr/local/bin/vgm-disk-check.sh

# Log rotation daily
0 0 * * * /usr/sbin/logrotate /etc/logrotate.d/vgm-website

# Database backup daily at 2 AM
0 2 * * * /opt/vgm-website/scripts/backup-db.sh
```

## Alert Notification Channels

### Email Notifications
```bash
# Configure email alerts
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=alerts@vgm-gent.be
MAIL_PASSWORD=your-app-password
```

### Slack Notifications
```bash
# Slack webhook URL
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### SMS Notifications (Optional)
```bash
# Twilio configuration for SMS alerts
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Monitoring Dashboard URLs

### Application Monitoring
- **Health Dashboard**: https://vgm-gent.be/health
- **API Status**: https://vgm-gent.be/api/health/ready
- **Sentry Dashboard**: https://sentry.io/organizations/vgm-gent/projects/

### Infrastructure Monitoring
- **Server Metrics**: SSH to server and run `htop`, `iotop`, `nethogs`
- **Database Metrics**: Connect to PostgreSQL and run monitoring queries
- **Log Files**: `/var/log/vgm-website/`

## Troubleshooting Guide

### Common Issues and Solutions

#### High Response Times
1. Check database query performance
2. Verify Redis cache is working
3. Check server resource usage
4. Review application logs for bottlenecks

#### High Error Rates
1. Check application logs for error patterns
2. Verify external service connectivity (Stripe, email)
3. Check database connection pool
4. Review recent deployments

#### Database Issues
1. Check database connection limits
2. Verify database server resources
3. Review slow query log
4. Check for database locks

#### Cache Issues
1. Verify Redis connectivity
2. Check cache hit rates
3. Review cache key expiration
4. Monitor Redis memory usage

## Performance Baselines

### Expected Performance Metrics
- **API Response Time**: < 500ms (95th percentile)
- **Page Load Time**: < 2 seconds
- **Database Query Time**: < 100ms (average)
- **Cache Hit Rate**: > 90%
- **Error Rate**: < 0.1%
- **Uptime**: > 99.9%

### Resource Usage Limits
- **CPU Usage**: < 70% (average)
- **Memory Usage**: < 80%
- **Disk Usage**: < 85%
- **Database Connections**: < 80% of pool
- **Redis Memory**: < 80% of allocated

---

**Note**: This monitoring configuration should be customized based on specific requirements and available monitoring tools in your environment.
