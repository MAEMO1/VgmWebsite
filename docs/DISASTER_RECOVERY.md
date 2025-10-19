# VGM Website - Disaster Recovery Runbook

## Overview
This document outlines the procedures for disaster recovery of the VGM Website platform, including database recovery, file restoration, and service restoration.

## Recovery Time Objectives (RTO) & Recovery Point Objectives (RPO)
- **RTO**: 4 hours (maximum downtime)
- **RPO**: 24 hours (maximum data loss)

## Backup Strategy

### Database Backups
- **Frequency**: Daily automated backups at 2:00 AM
- **Retention**: 30 days
- **Location**: `/backups/postgresql/`
- **Format**: Compressed SQL dumps
- **Script**: `scripts/backup-db.sh`

### File Backups
- **Upload files**: Daily sync to S3/Object Storage
- **Configuration files**: Version controlled in Git
- **Log files**: Rotated daily, retained for 30 days

### Application Backups
- **Code**: Git repository (GitHub)
- **Dependencies**: `requirements.txt` and `package.json`
- **Configuration**: Environment variables documented

## Disaster Scenarios & Recovery Procedures

### Scenario 1: Database Corruption/Loss

#### Symptoms
- Application errors related to database connectivity
- Data inconsistency errors
- Database service unavailable

#### Recovery Steps

1. **Immediate Response**
   ```bash
   # Check database status
   sudo systemctl status postgresql
   
   # Check database logs
   sudo tail -f /var/log/postgresql/postgresql-*.log
   ```

2. **Stop Application Services**
   ```bash
   sudo systemctl stop vgm-website
   sudo systemctl stop nginx
   ```

3. **Database Recovery**
   ```bash
   # List available backups
   ls -la /backups/postgresql/
   
   # Restore from most recent backup
   LATEST_BACKUP=$(ls -t /backups/postgresql/vgm_db_backup_*.sql.gz | head -1)
   
   # Drop and recreate database
   sudo -u postgres dropdb vgm_database
   sudo -u postgres createdb vgm_database
   
   # Restore from backup
   gunzip -c "$LATEST_BACKUP" | sudo -u postgres psql vgm_database
   ```

4. **Verify Database Integrity**
   ```bash
   # Check database connectivity
   psql -h localhost -U vgm_user -d vgm_database -c "SELECT COUNT(*) FROM users;"
   
   # Run database migrations if needed
   cd /opt/vgm-website
   source .venv/bin/activate
   alembic upgrade head
   ```

5. **Restart Services**
   ```bash
   sudo systemctl start vgm-website
   sudo systemctl start nginx
   ```

6. **Verify Application**
   ```bash
   # Check health endpoints
   curl http://localhost:5001/health
   curl http://localhost:5001/health/ready
   
   # Test critical functionality
   curl http://localhost:5001/api/mosques
   ```

### Scenario 2: Server Hardware Failure

#### Symptoms
- Server completely unresponsive
- Network connectivity lost
- Physical hardware issues

#### Recovery Steps

1. **Provision New Server**
   ```bash
   # Minimum server requirements
   - CPU: 2 cores
   - RAM: 4GB
   - Storage: 50GB SSD
   - OS: Ubuntu 20.04 LTS
   ```

2. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install PostgreSQL
   sudo apt install postgresql postgresql-contrib -y
   
   # Install Python 3.8+
   sudo apt install python3 python3-pip python3-venv -y
   
   # Install Node.js 20
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install nodejs -y
   
   # Install Redis
   sudo apt install redis-server -y
   
   # Install Nginx
   sudo apt install nginx -y
   ```

3. **Restore Application Code**
   ```bash
   # Clone repository
   git clone https://github.com/your-org/vgm-website.git /opt/vgm-website
   cd /opt/vgm-website
   
   # Install Python dependencies
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   
   # Install frontend dependencies
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Restore Database**
   ```bash
   # Create database and user
   sudo -u postgres createuser vgm_user
   sudo -u postgres createdb vgm_database
   sudo -u postgres psql -c "ALTER USER vgm_user PASSWORD 'vgm_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vgm_database TO vgm_user;"
   
   # Restore from backup (if available)
   # Or restore from S3/cloud storage
   ```

5. **Configure Services**
   ```bash
   # Copy configuration files
   sudo cp scripts/vgm-website.service /etc/systemd/system/
   sudo cp scripts/nginx.conf /etc/nginx/sites-available/vgm-website
   
   # Enable services
   sudo systemctl enable vgm-website
   sudo systemctl enable nginx
   sudo systemctl enable postgresql
   sudo systemctl enable redis
   ```

6. **Start Services**
   ```bash
   sudo systemctl start postgresql
   sudo systemctl start redis
   sudo systemctl start vgm-website
   sudo systemctl start nginx
   ```

### Scenario 3: Data Center Outage

#### Symptoms
- Complete loss of primary infrastructure
- No access to primary servers
- Extended downtime expected

#### Recovery Steps

1. **Activate Disaster Recovery Site**
   - Provision cloud instances (AWS/Azure/GCP)
   - Use infrastructure as code (Terraform/CloudFormation)

2. **Restore from Cloud Backups**
   ```bash
   # Database backup from S3
   aws s3 cp s3://vgm-backups/postgresql/latest.sql.gz ./
   gunzip latest.sql.gz
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME < latest.sql
   
   # File backups from S3
   aws s3 sync s3://vgm-backups/uploads/ ./uploads/
   ```

3. **Update DNS Records**
   - Point domain to new infrastructure
   - Update SSL certificates
   - Configure CDN if applicable

4. **Verify and Monitor**
   - Run health checks
   - Monitor application logs
   - Test critical user flows

## Testing Procedures

### Monthly Recovery Testing

1. **Database Recovery Test**
   ```bash
   # Create test database
   sudo -u postgres createdb vgm_test_recovery
   
   # Restore from backup
   gunzip -c /backups/postgresql/vgm_db_backup_$(date +%Y%m%d)*.sql.gz | \
   sudo -u postgres psql vgm_test_recovery
   
   # Verify data integrity
   psql -d vgm_test_recovery -c "SELECT COUNT(*) FROM users;"
   psql -d vgm_test_recovery -c "SELECT COUNT(*) FROM mosques;"
   
   # Clean up
   sudo -u postgres dropdb vgm_test_recovery
   ```

2. **Application Recovery Test**
   - Deploy to staging environment
   - Test all critical functionality
   - Verify performance metrics

### Quarterly Full Disaster Recovery Drill

1. **Simulate Complete Failure**
   - Shut down primary services
   - Simulate data loss
   - Test communication procedures

2. **Execute Recovery Plan**
   - Follow full recovery procedures
   - Document any issues or improvements
   - Update runbook based on findings

## Monitoring and Alerting

### Key Metrics to Monitor
- Database connectivity and performance
- Application response times
- Error rates and types
- Backup success/failure
- Disk space usage
- Memory and CPU utilization

### Alerting Thresholds
- Database down: Immediate alert
- Application errors > 5%: Alert within 15 minutes
- Response time > 2 seconds: Alert within 5 minutes
- Backup failure: Alert within 1 hour
- Disk space > 80%: Alert within 30 minutes

## Contact Information

### Primary Team
- **System Administrator**: admin@vgm-gent.be
- **Lead Developer**: dev@vgm-gent.be
- **Database Administrator**: dba@vgm-gent.be

### Escalation Procedures
1. **Level 1**: On-call developer (0-2 hours)
2. **Level 2**: Lead developer (2-4 hours)
3. **Level 3**: System administrator (4+ hours)

### External Contacts
- **Hosting Provider**: support@hosting-provider.com
- **Domain Registrar**: support@domain-registrar.com
- **CDN Provider**: support@cdn-provider.com

## Recovery Checklist

### Pre-Recovery
- [ ] Identify the scope of the disaster
- [ ] Notify stakeholders
- [ ] Gather necessary credentials and access
- [ ] Document current system state

### During Recovery
- [ ] Stop affected services
- [ ] Restore from backups
- [ ] Verify data integrity
- [ ] Test application functionality
- [ ] Monitor system performance

### Post-Recovery
- [ ] Verify all services are running
- [ ] Test critical user flows
- [ ] Monitor system for 24 hours
- [ ] Document lessons learned
- [ ] Update recovery procedures if needed
- [ ] Schedule post-incident review

## Appendices

### A. Backup Verification Script
```bash
#!/bin/bash
# Verify backup integrity
BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "Verifying backup: $BACKUP_FILE"
if gunzip -t "$BACKUP_FILE"; then
    echo "Backup file is valid"
else
    echo "Backup file is corrupted!"
    exit 1
fi
```

### B. Health Check Script
```bash
#!/bin/bash
# Comprehensive health check
echo "=== VGM Website Health Check ==="
echo "Date: $(date)"
echo

echo "1. Database Status:"
psql -h localhost -U vgm_user -d vgm_database -c "SELECT 'Database OK' as status;" 2>/dev/null || echo "Database ERROR"

echo "2. Application Status:"
curl -s http://localhost:5001/health | jq . || echo "Application ERROR"

echo "3. Redis Status:"
redis-cli ping 2>/dev/null || echo "Redis ERROR"

echo "4. Disk Space:"
df -h | grep -E "(/$|/opt)"

echo "5. Memory Usage:"
free -h

echo "6. Recent Errors:"
tail -n 20 /var/log/vgm-website/error.log 2>/dev/null || echo "No error log found"
```

### C. Emergency Contacts
- **24/7 Support**: +32-XXX-XXX-XXX
- **Emergency Email**: emergency@vgm-gent.be
- **Slack Channel**: #vgm-emergency
- **Status Page**: https://status.vgm-gent.be
