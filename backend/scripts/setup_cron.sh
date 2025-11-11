#!/bin/bash
# ============================================
# Pulse of People - Automated Backup Setup
# Configure cron jobs for automated backups
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_SCRIPT="${SCRIPT_DIR}/backup_database.sh"

echo "Setting up automated database backups..."

# Make backup script executable
chmod +x "$BACKUP_SCRIPT"

# Create cron job (daily at 2 AM)
CRON_JOB="0 2 * * * $BACKUP_SCRIPT >> /var/log/pulseofpeople/backup.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "Cron job already exists. Updating..."
    crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Automated backup scheduled:"
echo "  Schedule: Daily at 2:00 AM"
echo "  Script: $BACKUP_SCRIPT"
echo "  Logs: /var/log/pulseofpeople/backup.log"
echo ""
echo "Current crontab:"
crontab -l

echo ""
echo "Setup complete!"
