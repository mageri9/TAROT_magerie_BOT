#!/bin/bash
# PostgreSQL backup with integrity check and 7-day retention

set -e

BACKUP_DIR="/root/backups"
DB_CONTAINER="tarot_magerie_bot-postgres-1"
DB_NAME="tarot_bot"
DB_USER="bot_user"
RETENTION_DAYS=7
LOG_FILE="$BACKUP_DIR/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M)
BACKUP_FILE="$BACKUP_DIR/tarot_$TIMESTAMP.sql.gz"

log "🚀 Starting backup..."

# Dump + compress
if docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    log "✅ Dump created: $BACKUP_FILE"
else
    log "❌ Dump failed"
    exit 1
fi

# Integrity check
if [ ! -s "$BACKUP_FILE" ]; then
    log "❌ Backup file is empty!"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Symlink to latest
ln -sf "$BACKUP_FILE" "$BACKUP_DIR/tarot_latest.sql.gz"
log "🔗 Symlink updated"

# Delete old backups
find "$BACKUP_DIR" -name "tarot_*.sql.gz" -mtime +$RETENTION_DAYS -delete
log "🧹 Old backups cleaned"

# Stats
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log "📦 Size: $SIZE"
log "✨ Backup completed"