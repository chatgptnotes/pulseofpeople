#!/bin/bash
# ============================================
# Pulse of People - Database Backup Script
# Automated PostgreSQL backup with S3 upload
# ============================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# ============================================
# Configuration
# ============================================

# Load environment variables
if [ -f ../.env ]; then
    source ../.env
fi

# Backup settings
BACKUP_DIR="${BACKUP_DIR:-/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
S3_BUCKET="${BACKUP_S3_BUCKET:-pulseofpeople-backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="db_backup_${DATE}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

# Database settings
DB_NAME="${DB_NAME:-pulseofpeople}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Notification settings
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
BACKUP_ADMIN_EMAIL="${BACKUP_ADMIN_EMAIL:-admin@pulseofpeople.com}"

# ============================================
# Functions
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

send_notification() {
    local message="$1"
    local status="$2"  # success or error

    # Slack notification
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local color="good"
        if [ "$status" = "error" ]; then
            color="danger"
        fi

        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"$message\",\"color\":\"$color\"}" \
            || log "Failed to send Slack notification"
    fi

    # Email notification (if sendmail is available)
    if command -v sendmail &> /dev/null; then
        echo "$message" | sendmail "$BACKUP_ADMIN_EMAIL" || log "Failed to send email notification"
    fi
}

cleanup_old_backups() {
    log "Cleaning up local backups older than ${BACKUP_RETENTION_DAYS} days..."
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete || true

    log "Cleaning up S3 backups older than ${BACKUP_RETENTION_DAYS} days..."
    if command -v aws &> /dev/null; then
        aws s3 ls "s3://${S3_BUCKET}/" | while read -r line; do
            createDate=$(echo "$line" | awk '{print $1" "$2}')
            createDate=$(date -d "$createDate" +%s 2>/dev/null || date -j -f "%Y-%m-%d %H:%M:%S" "$createDate" +%s 2>/dev/null || echo "0")
            olderThan=$(date -d "${BACKUP_RETENTION_DAYS} days ago" +%s 2>/dev/null || date -j -v-${BACKUP_RETENTION_DAYS}d +%s 2>/dev/null || echo "0")

            if [[ $createDate -lt $olderThan ]] && [[ $createDate -ne 0 ]]; then
                fileName=$(echo "$line" | awk '{print $4}')
                if [ -n "$fileName" ] && [[ "$fileName" == db_backup_* ]]; then
                    log "Deleting old backup: $fileName"
                    aws s3 rm "s3://${S3_BUCKET}/$fileName" || log "Failed to delete $fileName"
                fi
            fi
        done
    fi
}

# ============================================
# Main Backup Process
# ============================================

log "Starting database backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform database dump
log "Creating PostgreSQL dump..."
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-owner \
    --no-acl \
    --clean \
    --if-exists \
    -f "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -ne 0 ]; then
    log "ERROR: Database dump failed!"
    send_notification "Database backup failed for ${DB_NAME}" "error"
    exit 1
fi

log "Database dump created successfully"

# Compress the backup
log "Compressing backup..."
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -ne 0 ]; then
    log "ERROR: Compression failed!"
    send_notification "Backup compression failed" "error"
    exit 1
fi

# Get compressed file size
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${COMPRESSED_FILE}" | cut -f1)
log "Compressed backup size: ${BACKUP_SIZE}"

# Upload to S3 (if AWS CLI is available)
if command -v aws &> /dev/null; then
    log "Uploading backup to S3..."
    aws s3 cp "${BACKUP_DIR}/${COMPRESSED_FILE}" "s3://${S3_BUCKET}/" \
        --storage-class STANDARD_IA \
        --metadata "db_name=${DB_NAME},backup_date=${DATE}" \
        || log "WARNING: S3 upload failed"

    if [ $? -eq 0 ]; then
        log "Backup uploaded to S3 successfully"
    fi
else
    log "WARNING: AWS CLI not found, skipping S3 upload"
fi

# Cleanup old backups
cleanup_old_backups

# Send success notification
log "Backup completed successfully!"
send_notification "Database backup completed successfully. File: ${COMPRESSED_FILE}, Size: ${BACKUP_SIZE}" "success"

# Print backup information
cat <<EOF

========================================
BACKUP SUMMARY
========================================
Database: ${DB_NAME}
Date: ${DATE}
File: ${COMPRESSED_FILE}
Size: ${BACKUP_SIZE}
Location: ${BACKUP_DIR}/${COMPRESSED_FILE}
S3: s3://${S3_BUCKET}/${COMPRESSED_FILE}
========================================

EOF

exit 0
