#!/bin/bash
# ============================================
# Pulse of People - Database Restore Script
# Restore PostgreSQL database from backup
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
S3_BUCKET="${BACKUP_S3_BUCKET:-pulseofpeople-backups}"

# Database settings
DB_NAME="${DB_NAME:-pulseofpeople}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# ============================================
# Functions
# ============================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <backup_file>

Restore PostgreSQL database from backup file.

Arguments:
    backup_file     Path to backup file (.sql or .sql.gz)
                   Can be local path or S3 URL (s3://bucket/file)

Options:
    -h, --help      Show this help message
    -f, --force     Skip confirmation prompt
    -l, --list      List available backups
    --latest        Use the latest available backup

Examples:
    # Restore from local file
    $0 /backups/db_backup_20231109_120000.sql.gz

    # Restore from S3
    $0 s3://pulseofpeople-backups/db_backup_20231109_120000.sql.gz

    # List available backups
    $0 --list

    # Restore latest backup without confirmation
    $0 --latest --force

EOF
    exit 1
}

list_backups() {
    log "Available local backups:"
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | awk '{print $9, "(" $5 ")", $6, $7, $8}' || echo "No local backups found"
    else
        echo "Backup directory not found: $BACKUP_DIR"
    fi

    echo ""
    log "Available S3 backups:"
    if command -v aws &> /dev/null; then
        aws s3 ls "s3://${S3_BUCKET}/" --human-readable | grep db_backup_ || echo "No S3 backups found"
    else
        echo "AWS CLI not available"
    fi

    exit 0
}

get_latest_backup() {
    local latest_local=""
    local latest_s3=""

    # Check local backups
    if [ -d "$BACKUP_DIR" ]; then
        latest_local=$(ls -t "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | head -n1)
    fi

    # Check S3 backups
    if command -v aws &> /dev/null; then
        latest_s3=$(aws s3 ls "s3://${S3_BUCKET}/" | grep db_backup_ | sort -r | head -n1 | awk '{print $4}')
        if [ -n "$latest_s3" ]; then
            latest_s3="s3://${S3_BUCKET}/${latest_s3}"
        fi
    fi

    # Return the most recent
    if [ -n "$latest_local" ] && [ -n "$latest_s3" ]; then
        # Compare timestamps (simplified - use local if both exist)
        echo "$latest_local"
    elif [ -n "$latest_local" ]; then
        echo "$latest_local"
    elif [ -n "$latest_s3" ]; then
        echo "$latest_s3"
    else
        log "ERROR: No backups found!"
        exit 1
    fi
}

confirm_restore() {
    local backup_file="$1"

    echo ""
    echo "========================================="
    echo "WARNING: DATABASE RESTORE"
    echo "========================================="
    echo "This will restore the database from:"
    echo "  $backup_file"
    echo ""
    echo "Current database will be DROPPED and replaced!"
    echo "Database: $DB_NAME"
    echo "Host: $DB_HOST"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled by user"
        exit 0
    fi
}

restore_from_file() {
    local backup_file="$1"
    local temp_file=""

    log "Starting database restore from: $backup_file"

    # Download from S3 if needed
    if [[ "$backup_file" == s3://* ]]; then
        if ! command -v aws &> /dev/null; then
            log "ERROR: AWS CLI is required to restore from S3"
            exit 1
        fi

        temp_file="${BACKUP_DIR}/temp_restore_$(date +%s).sql.gz"
        log "Downloading backup from S3..."
        aws s3 cp "$backup_file" "$temp_file"

        if [ $? -ne 0 ]; then
            log "ERROR: Failed to download backup from S3"
            exit 1
        fi

        backup_file="$temp_file"
    fi

    # Verify file exists
    if [ ! -f "$backup_file" ]; then
        log "ERROR: Backup file not found: $backup_file"
        exit 1
    fi

    log "Backup file size: $(du -h "$backup_file" | cut -f1)"

    # Create a pre-restore backup
    log "Creating pre-restore backup as safety measure..."
    SAFETY_BACKUP="${BACKUP_DIR}/pre_restore_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-owner \
        --no-acl \
        | gzip > "$SAFETY_BACKUP" || log "WARNING: Pre-restore backup failed"

    # Stop application services (optional - uncomment if needed)
    # systemctl stop pulseofpeople-backend || true
    # docker-compose stop backend celery celery-beat || true

    # Restore database
    log "Restoring database..."

    if [[ "$backup_file" == *.gz ]]; then
        # Compressed backup
        gunzip -c "$backup_file" | PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            --set ON_ERROR_STOP=on
    else
        # Uncompressed backup
        PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME" \
            --set ON_ERROR_STOP=on \
            -f "$backup_file"
    fi

    if [ $? -ne 0 ]; then
        log "ERROR: Database restore failed!"
        log "Safety backup available at: $SAFETY_BACKUP"
        exit 1
    fi

    # Cleanup temp file
    if [ -n "$temp_file" ] && [ -f "$temp_file" ]; then
        rm -f "$temp_file"
    fi

    # Restart application services (optional - uncomment if needed)
    # systemctl start pulseofpeople-backend || true
    # docker-compose start backend celery celery-beat || true

    log "Database restored successfully!"
    log "Pre-restore backup saved at: $SAFETY_BACKUP"

    # Print restore summary
    cat <<EOF

========================================
RESTORE SUMMARY
========================================
Database: ${DB_NAME}
Host: ${DB_HOST}
Restored from: ${backup_file}
Date: $(date)
Pre-restore backup: ${SAFETY_BACKUP}
========================================

EOF
}

# ============================================
# Main Script
# ============================================

BACKUP_FILE=""
FORCE=false
USE_LATEST=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            ;;
        -l|--list)
            list_backups
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        --latest)
            USE_LATEST=true
            shift
            ;;
        -*)
            log "ERROR: Unknown option: $1"
            show_usage
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# Get latest backup if requested
if [ "$USE_LATEST" = true ]; then
    BACKUP_FILE=$(get_latest_backup)
    log "Using latest backup: $BACKUP_FILE"
fi

# Validate backup file
if [ -z "$BACKUP_FILE" ]; then
    log "ERROR: No backup file specified"
    show_usage
fi

# Confirm restore
if [ "$FORCE" != true ]; then
    confirm_restore "$BACKUP_FILE"
fi

# Perform restore
restore_from_file "$BACKUP_FILE"

exit 0
