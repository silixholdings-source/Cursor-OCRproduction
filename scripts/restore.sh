#!/bin/bash
# Bash script for restoring AI ERP SaaS application from backup
# This script restores PostgreSQL, Redis, and application files

# Exit on error
set -e

# Check if backup archive is provided
if [ -z "$1" ]; then
    echo "Error: Backup archive path not provided"
    echo "Usage: $0 <backup_archive_path>"
    exit 1
fi

BACKUP_ARCHIVE="$1"

# Configuration
POSTGRES_CONTAINER="ai-erp-postgres-dev"
REDIS_CONTAINER="ai-erp-redis-dev"
TEMP_DIR="./temp_restore"

# Check if backup archive exists
if [ ! -f "$BACKUP_ARCHIVE" ]; then
    echo "Error: Backup archive not found: $BACKUP_ARCHIVE"
    exit 1
fi

# Create temporary directory
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi
mkdir -p "$TEMP_DIR"
echo "Created temporary directory: $TEMP_DIR"

# Extract backup archive
echo "Extracting backup archive..."
tar -xzf "$BACKUP_ARCHIVE" -C "$TEMP_DIR"
BACKUP_DIR="$TEMP_DIR/$(ls -1 $TEMP_DIR | head -1)"
echo "Extracted backup to: $BACKUP_DIR"

# Restore PostgreSQL database
echo "Restoring PostgreSQL database..."
cat "$BACKUP_DIR/postgres_dump.sql" | docker exec -i $POSTGRES_CONTAINER psql -U postgres -d ai_erp_saas
if [ $? -eq 0 ]; then
    echo "PostgreSQL restore completed successfully"
else
    echo "PostgreSQL restore failed with exit code $?"
    exit 1
fi

# Restore Redis data
echo "Restoring Redis data..."
docker cp "$BACKUP_DIR/redis_dump.rdb" "$REDIS_CONTAINER:/data/dump.rdb"
docker exec $REDIS_CONTAINER redis-cli SHUTDOWN SAVE
if [ $? -eq 0 ]; then
    echo "Redis restore completed successfully"
else
    echo "Redis restore failed with exit code $?"
    exit 1
fi

# Restore application files
echo "Restoring application files..."
declare -A DIRS_TO_RESTORE=(
    ["$BACKUP_DIR/src"]="./backend/src"
    ["$BACKUP_DIR/models"]="./backend/models"
    ["$BACKUP_DIR/uploads"]="./backend/uploads"
    ["$BACKUP_DIR/src"]="./web/src"
)

for SRC in "${!DIRS_TO_RESTORE[@]}"; do
    DEST="${DIRS_TO_RESTORE[$SRC]}"
    if [ -d "$SRC" ]; then
        cp -r "$SRC"/* "$DEST"
    else
        echo "Warning: Source directory not found: $SRC"
    fi
done
echo "Application files restore completed successfully"

# Clean up
echo "Cleaning up temporary files..."
rm -rf "$TEMP_DIR"
echo "Cleanup completed"

echo "Restore completed from: $BACKUP_ARCHIVE"