#!/bin/bash
# Bash script for backing up AI ERP SaaS application
# This script backs up PostgreSQL, Redis, and application files

# Exit on error
set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ai-erp-saas_backup_$TIMESTAMP"
POSTGRES_CONTAINER="ai-erp-postgres-dev"
REDIS_CONTAINER="ai-erp-redis-dev"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Create timestamp directory
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
mkdir -p "$BACKUP_PATH"
echo "Created backup directory: $BACKUP_PATH"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
docker exec $POSTGRES_CONTAINER pg_dump -U postgres -d ai_erp_saas > "$BACKUP_PATH/postgres_dump.sql"
if [ $? -eq 0 ]; then
    echo "PostgreSQL backup completed successfully"
else
    echo "PostgreSQL backup failed with exit code $?"
    exit 1
fi

# Backup Redis data
echo "Backing up Redis data..."
docker exec $REDIS_CONTAINER redis-cli SAVE
docker cp "$REDIS_CONTAINER:/data/dump.rdb" "$BACKUP_PATH/redis_dump.rdb"
if [ $? -eq 0 ]; then
    echo "Redis backup completed successfully"
else
    echo "Redis backup failed with exit code $?"
    exit 1
fi

# Backup application files
echo "Backing up application files..."
DIRS_TO_BACKUP=(
    "./backend/src"
    "./backend/models"
    "./backend/uploads"
    "./web/src"
)

for DIR in "${DIRS_TO_BACKUP[@]}"; do
    TARGET_DIR="$BACKUP_PATH/$(basename $DIR)"
    mkdir -p "$TARGET_DIR"
    cp -r "$DIR"/* "$TARGET_DIR"
done
echo "Application files backup completed successfully"

# Create a compressed archive
echo "Creating compressed backup archive..."
tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "$BACKUP_NAME"
if [ $? -eq 0 ]; then
    echo "Backup archive created successfully: $BACKUP_PATH.tar.gz"
else
    echo "Failed to create backup archive"
    exit 1
fi

echo "Backup completed: $BACKUP_PATH.tar.gz"