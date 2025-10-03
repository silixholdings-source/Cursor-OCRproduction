# AI ERP SaaS Development Environment Setup Script for Windows
# Run this script in PowerShell as Administrator

param(
    [switch]$SkipDockerCheck,
    [switch]$SkipTests,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Header {
    param([string]$Message)
    Write-ColorOutput "`n" -Color Info
    Write-ColorOutput ("=" * 60) -Color Header
    Write-ColorOutput $Message -Color Header
    Write-ColorOutput ("=" * 60) -Color Header
    Write-ColorOutput "`n" -Color Info
}

function Write-Success { param([string]$Message) Write-ColorOutput "SUCCESS: $Message" -Color Success }
function Write-Error { param([string]$Message) Write-ColorOutput "ERROR: $Message" -Color Error }
function Write-Warning { param([string]$Message) Write-ColorOutput "WARNING: $Message" -Color Warning }
function Write-Info { param([string]$Message) Write-ColorOutput "INFO: $Message" -Color Info }

# Main setup function
function Setup-DevelopmentEnvironment {
    Write-Header "AI ERP SaaS Development Environment Setup"
    
    # Check if running as Administrator
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Error "This script must be run as Administrator. Please right-click PowerShell and select 'Run as Administrator'."
        exit 1
    }
    
    # Step 1: Check Docker
    if (-not $SkipDockerCheck) {
        Write-Header "Step 1: Docker Environment Check"
        
        # Check if Docker Desktop is installed
        $dockerPath = Get-Command docker -ErrorAction SilentlyContinue
        if (-not $dockerPath) {
            Write-Warning "Docker not found in PATH. Checking for Docker Desktop installation..."
            
            # Check common Docker Desktop installation paths
            $dockerDesktopPaths = @(
                "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe",
                "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe"
            )
            
            $dockerInstalled = $false
            foreach ($path in $dockerDesktopPaths) {
                if (Test-Path $path) {
                    Write-Info "Docker Desktop found at: $path"
                    $dockerInstalled = $true
                    break
                }
            }
            
            if (-not $dockerInstalled) {
                Write-Error "Docker Desktop not found. Please install Docker Desktop first:"
                Write-Info "1. Download from: https://www.docker.com/products/docker-desktop"
                Write-Info "2. Install and restart your computer"
                Write-Info "3. Start Docker Desktop"
                Write-Info "4. Run this script again"
                exit 1
            }
            
            # Try to start Docker Desktop
            Write-Info "Attempting to start Docker Desktop..."
            try {
                Start-Process "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe" -ErrorAction Stop
                Write-Info "Docker Desktop started. Waiting for it to be ready..."
                
                # Wait for Docker to be ready
                $maxWait = 120  # 2 minutes
                $waitTime = 0
                while ($waitTime -lt $maxWait) {
                    try {
                        $null = docker info 2>$null
                        if ($LASTEXITCODE -eq 0) {
                            Write-Success "Docker is ready!"
                            break
                        }
                    } catch {
                        # Docker not ready yet
                    }
                    
                    Start-Sleep -Seconds 2
                    $waitTime += 2
                    Write-Info "Waiting for Docker... ($waitTime of $maxWait seconds)"
                }
                
                if ($waitTime -ge $maxWait) {
                    Write-Error "Docker Desktop took too long to start. Please start it manually and run this script again."
                    exit 1
                }
            } catch {
                Write-Error "Failed to start Docker Desktop automatically. Please start it manually and run this script again."
                exit 1
            }
        } else {
            Write-Success "Docker found in PATH"
        }
        
        # Verify Docker is running
        try {
            $dockerInfo = docker info 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker daemon is running"
            } else {
                Write-Error "Docker daemon is not running. Please start Docker Desktop."
                exit 1
            }
        } catch {
            Write-Error "Failed to communicate with Docker daemon. Please start Docker Desktop."
            exit 1
        }
        
        # Check Docker Compose
        try {
            $dockerComposeVersion = docker-compose --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker Compose available: $dockerComposeVersion"
            } else {
                Write-Error "Docker Compose not available. Please install Docker Compose."
                exit 1
            }
        } catch {
            Write-Error "Failed to check Docker Compose. Please install Docker Compose."
            exit 1
        }
    }
    
    # Step 2: Build Docker Images
    Write-Header "Step 2: Building Docker Images"
    
    try {
        Write-Info "Building Docker images (this may take several minutes)..."
        $buildOutput = docker-compose -f docker-compose.dev.yml build --no-cache 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker images built successfully"
            if ($Verbose) {
                Write-Info "Build output: $buildOutput"
            }
        } else {
            Write-Error "Failed to build Docker images: $buildOutput"
            exit 1
        }
    } catch {
        Write-Error "Exception during Docker build: $($_.Exception.Message)"
        exit 1
    }
    
    # Step 3: Start Infrastructure
    Write-Header "Step 3: Starting Infrastructure Services"
    
    try {
        Write-Info "Starting PostgreSQL and Redis..."
        $startOutput = docker-compose -f docker-compose.dev.yml up -d postgres redis 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Infrastructure services started"
            if ($Verbose) {
                Write-Info "Start output: $startOutput"
            }
        } else {
            Write-Error "Failed to start infrastructure services: $startOutput"
            exit 1
        }
    } catch {
        Write-Error "Exception starting infrastructure: $($_.Exception.Message)"
        exit 1
    }
    
    # Step 4: Wait for Services
    Write-Header "Step 4: Waiting for Services to be Ready"
    
    Write-Info "Waiting for PostgreSQL to be ready..."
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $pgReady = docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PostgreSQL is ready"
                break
            }
        } catch {
            # Service not ready yet
        }
        
        $attempt++
        Write-Info "Waiting for PostgreSQL... (attempt $attempt of $maxAttempts)"
        Start-Sleep -Seconds 2
    }
    
    if ($attempt -ge $maxAttempts) {
        Write-Error "PostgreSQL failed to become ready"
        exit 1
    }
    
    Write-Info "Waiting for Redis to be ready..."
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            $redisReady = docker-compose -f docker-compose.dev.yml exec redis redis-cli ping 2>$null
            if ($LASTEXITCODE -eq 0 -and $redisReady -eq "PONG") {
                Write-Success "Redis is ready"
                break
            }
        } catch {
            # Service not ready yet
        }
        
        $attempt++
        Write-Info "Waiting for Redis... (attempt $attempt of $maxAttempts)"
        Start-Sleep -Seconds 2
    }
    
    if ($attempt -ge $maxAttempts) {
        Write-Error "Redis failed to become ready"
        exit 1
    }
    
    # Step 5: Run Migrations
    Write-Header "Step 5: Running Database Migrations"
    
    try {
        Write-Info "Running database migrations..."
        $migrationOutput = docker-compose -f docker-compose.dev.yml run --rm backend python -m alembic upgrade head 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database migrations completed"
            if ($Verbose) {
                Write-Info "Migration output: $migrationOutput"
            }
        } else {
            Write-Error "Database migrations failed: $migrationOutput"
            exit 1
        }
    } catch {
        Write-Error "Exception during migrations: $($_.Exception.Message)"
        exit 1
    }
    
    # Step 6: Create Tables
    Write-Header "Step 6: Creating Database Tables"
    
    try {
        Write-Info "Creating database tables..."
        $tableOutput = docker-compose -f docker-compose.dev.yml run --rm backend python -c "
from src.core.database import engine
from src.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database tables created"
            if ($Verbose) {
                Write-Info "Table creation output: $tableOutput"
            }
        } else {
            Write-Error "Failed to create database tables: $tableOutput"
            exit 1
        }
    } catch {
        Write-Error "Exception creating tables: $($_.Exception.Message)"
        exit 1
    }
    
    # Step 7: Start Application
    Write-Header "Step 7: Starting Application Services"
    
    try {
        Write-Info "Starting backend, web frontend, and worker services..."
        $appOutput = docker-compose -f docker-compose.dev.yml up -d backend web worker 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Application services started"
            if ($Verbose) {
                Write-Info "Application start output: $appOutput"
            }
        } else {
            Write-Error "Failed to start application services: $appOutput"
            exit 1
        }
    } catch {
        Write-Error "Exception starting application: $($_.Exception.Message)"
        exit 1
    }
    
    # Step 8: Health Checks
    Write-Header "Step 8: Running Health Checks"
    
    Write-Info "Waiting for services to fully start..."
    Start-Sleep -Seconds 10
    
    # Check backend health
    Write-Info "Checking backend API health..."
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($healthResponse.StatusCode -eq 200) {
            Write-Success "Backend API is healthy"
        } else {
            Write-Error "Backend API health check failed with status: $($healthResponse.StatusCode)"
        }
    } catch {
        Write-Error "Backend API health check failed: $($_.Exception.Message)"
    }
    
    # Check database health
    Write-Info "Checking database health..."
    try {
        $dbHealth = docker-compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database is healthy"
        } else {
            Write-Error "Database health check failed"
        }
    } catch {
        Write-Error "Database health check failed: $($_.Exception.Message)"
    }
    
    # Check Redis health
    Write-Info "Checking Redis health..."
    try {
        $redisHealth = docker-compose -f docker-compose.dev.yml exec redis redis-cli ping 2>$null
        if ($LASTEXITCODE -eq 0 -and $redisHealth -eq "PONG") {
            Write-Success "Redis is healthy"
        } else {
            Write-Error "Redis health check failed"
        }
    } catch {
        Write-Error "Redis health check failed: $($_.Exception.Message)"
    }
    
    # Step 9: Run Tests (Optional)
    if (-not $SkipTests) {
        Write-Header "Step 9: Running Initial Tests"
        
        try {
            Write-Info "Running initial smoke tests..."
            $testOutput = docker-compose -f docker-compose.dev.yml run --rm test-runner pytest tests/unit/test_health.py -v 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Initial tests passed"
                if ($Verbose) {
                    Write-Info "Test output: $testOutput"
                }
            } else {
                Write-Warning "Initial tests failed: $testOutput"
                Write-Info "This is not critical for setup, but you may want to investigate later"
            }
        } catch {
            Write-Warning "Exception during initial tests: $($_.Exception.Message)"
            Write-Info "This is not critical for setup, but you may want to investigate later"
        }
    }
    
    # Final Summary
    Write-Header "Setup Complete!"
    
    Write-Success "Your AI ERP SaaS development environment is now running!"
    Write-Info ""
    Write-Info "Services available at:"
    Write-Info "  * Backend API: http://localhost:8000"
    Write-Info "  * API Documentation: http://localhost:8000/docs"
    Write-Info "  * Web Frontend: http://localhost:3000"
    Write-Info "  * Database: localhost:5432"
    Write-Info "  * Redis: localhost:6379"
    Write-Info ""
    Write-Info "Quick commands:"
    Write-Info "  * View logs: docker-compose -f docker-compose.dev.yml logs -f"
    Write-Info "  * Stop services: docker-compose -f docker-compose.dev.yml down"
    Write-Info "  * Restart: docker-compose -f docker-compose.dev.yml restart"
    Write-Info "  * Run tests: docker-compose -f docker-compose.dev.yml run --rm test-runner pytest"
    Write-Info ""
    Write-Info "For more commands, see: DEV_README.md"
    Write-Info ""
    Write-Success "Happy coding!"
}

# Main execution
try {
    Setup-DevelopmentEnvironment
} catch {
    Write-Error "Setup failed with exception: $($_.Exception.Message)"
    Write-Info "Please check the error details above and try again"
    exit 1
}












