# PowerShell script for backing up AI ERP SaaS application
# This script backs up PostgreSQL, Redis, and application files

# Configuration
$BACKUP_DIR = ".\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_NAME = "ai-erp-saas_backup_$TIMESTAMP"
$POSTGRES_CONTAINER = "ai-erp-postgres-dev"
$REDIS_CONTAINER = "ai-erp-redis-dev"

# Create backup directory if it doesn't exist
if (-not (Test-Path -Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
    Write-Host "Created backup directory: $BACKUP_DIR"
}

# Create timestamp directory
$BACKUP_PATH = Join-Path -Path $BACKUP_DIR -ChildPath $BACKUP_NAME
New-Item -ItemType Directory -Path $BACKUP_PATH | Out-Null
Write-Host "Created backup directory: $BACKUP_PATH"

# Backup PostgreSQL database
Write-Host "Backing up PostgreSQL database..."
docker exec $POSTGRES_CONTAINER pg_dump -U postgres -d ai_erp_saas > "$BACKUP_PATH\postgres_dump.sql"
if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL backup completed successfully"
} else {
    Write-Host "PostgreSQL backup failed with exit code $LASTEXITCODE"
}

# Backup Redis data
Write-Host "Backing up Redis data..."
docker exec $REDIS_CONTAINER redis-cli SAVE
docker cp "${REDIS_CONTAINER}:/data/dump.rdb" "$BACKUP_PATH\redis_dump.rdb"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Redis backup completed successfully"
} else {
    Write-Host "Redis backup failed with exit code $LASTEXITCODE"
}

# Backup application files
Write-Host "Backing up application files..."
$DIRS_TO_BACKUP = @(
    ".\backend\src",
    ".\backend\models",
    ".\backend\uploads",
    ".\web\src"
)

foreach ($DIR in $DIRS_TO_BACKUP) {
    $TARGET_DIR = Join-Path -Path $BACKUP_PATH -ChildPath (Split-Path -Path $DIR -Leaf)
    New-Item -ItemType Directory -Path $TARGET_DIR -Force | Out-Null
    Copy-Item -Path "$DIR\*" -Destination $TARGET_DIR -Recurse -Force
}
Write-Host "Application files backup completed successfully"

# Create a compressed archive
Write-Host "Creating compressed backup archive..."
Compress-Archive -Path $BACKUP_PATH -DestinationPath "$BACKUP_PATH.zip"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup archive created successfully: $BACKUP_PATH.zip"
} else {
    Write-Host "Failed to create backup archive"
}

Write-Host "Backup completed: $BACKUP_PATH.zip"