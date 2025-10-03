# PowerShell script for restoring AI ERP SaaS application from backup
# This script restores PostgreSQL, Redis, and application files

param (
    [Parameter(Mandatory=$true)]
    [string]$BackupArchive
)

# Configuration
$POSTGRES_CONTAINER = "ai-erp-postgres-dev"
$REDIS_CONTAINER = "ai-erp-redis-dev"
$TEMP_DIR = ".\temp_restore"

# Check if backup archive exists
if (-not (Test-Path -Path $BackupArchive)) {
    Write-Host "Error: Backup archive not found: $BackupArchive"
    exit 1
}

# Create temporary directory
if (Test-Path -Path $TEMP_DIR) {
    Remove-Item -Path $TEMP_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null
Write-Host "Created temporary directory: $TEMP_DIR"

# Extract backup archive
Write-Host "Extracting backup archive..."
Expand-Archive -Path $BackupArchive -DestinationPath $TEMP_DIR
$BACKUP_DIR = Get-ChildItem -Path $TEMP_DIR | Select-Object -First 1 -ExpandProperty FullName
Write-Host "Extracted backup to: $BACKUP_DIR"

# Restore PostgreSQL database
Write-Host "Restoring PostgreSQL database..."
Get-Content "$BACKUP_DIR\postgres_dump.sql" | docker exec -i $POSTGRES_CONTAINER psql -U postgres -d ai_erp_saas
if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL restore completed successfully"
} else {
    Write-Host "PostgreSQL restore failed with exit code $LASTEXITCODE"
}

# Restore Redis data
Write-Host "Restoring Redis data..."
docker cp "${BACKUP_DIR}\redis_dump.rdb" "${REDIS_CONTAINER}:/data/dump.rdb"
docker exec $REDIS_CONTAINER redis-cli SHUTDOWN SAVE
if ($LASTEXITCODE -eq 0) {
    Write-Host "Redis restore completed successfully"
} else {
    Write-Host "Redis restore failed with exit code $LASTEXITCODE"
}

# Restore application files
Write-Host "Restoring application files..."
$DIRS_TO_RESTORE = @(
    @{Source="$BACKUP_DIR\src"; Destination=".\backend\src"},
    @{Source="$BACKUP_DIR\models"; Destination=".\backend\models"},
    @{Source="$BACKUP_DIR\uploads"; Destination=".\backend\uploads"},
    @{Source="$BACKUP_DIR\src"; Destination=".\web\src"}
)

foreach ($DIR in $DIRS_TO_RESTORE) {
    if (Test-Path -Path $DIR.Source) {
        Copy-Item -Path "$($DIR.Source)\*" -Destination $DIR.Destination -Recurse -Force
    } else {
        Write-Host "Warning: Source directory not found: $($DIR.Source)"
    }
}
Write-Host "Application files restore completed successfully"

# Clean up
Write-Host "Cleaning up temporary files..."
Remove-Item -Path $TEMP_DIR -Recurse -Force
Write-Host "Cleanup completed"

Write-Host "Restore completed from: $BackupArchive"