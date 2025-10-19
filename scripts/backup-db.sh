#!/bin/bash
# PostgreSQL backup script for VGM Website
# Run daily via cron: 0 2 * * * /path/to/backup-db.sh

set -e

# Configuration
DB_NAME=${DB_NAME:-"vgm_database"}
DB_USER=${DB_USER:-"vgm_user"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
BACKUP_DIR=${BACKUP_DIR:-"/backups/postgresql"}
RETENTION_DAYS=${RETENTION_DAYS:-30}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/vgm_db_backup_${DATE}.sql"
LOG_FILE="/var/log/vgm-backup.log"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting PostgreSQL backup for database: $DB_NAME"

# Perform backup
if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --verbose --clean --no-owner --no-privileges \
    --format=plain > "$BACKUP_FILE" 2>> "$LOG_FILE"; then
    
    # Compress backup
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    # Get file size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    
    log "Backup completed successfully: $BACKUP_FILE (Size: $BACKUP_SIZE)"
    
    # Clean up old backups
    log "Cleaning up backups older than $RETENTION_DAYS days"
    find "$BACKUP_DIR" -name "vgm_db_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # Count remaining backups
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "vgm_db_backup_*.sql.gz" -type f | wc -l)
    log "Backup retention: $BACKUP_COUNT backups remaining"
    
else
    log "ERROR: Backup failed!"
    exit 1
fi

log "PostgreSQL backup process completed"
