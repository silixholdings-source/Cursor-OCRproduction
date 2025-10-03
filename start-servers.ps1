# AI ERP SaaS Application Launcher - PowerShell Version
# Fixed version without && syntax errors

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    AI ERP SaaS Application Launcher" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "[CHECKING] Prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "python")) {
    Write-Host "✗ Python not found. Please install Python." -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "npm")) {
    Write-Host "✗ Node.js/npm not found. Please install Node.js." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python and Node.js are available" -ForegroundColor Green

# Clean up any existing processes on our ports
Write-Host ""
Write-Host "[CLEANUP] Checking for existing processes..." -ForegroundColor Yellow

try {
    $processes3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    if ($processes3000) {
        $processes3000 | ForEach-Object {
            $processId = $_.OwningProcess
            Write-Host "Stopping process $processId on port 3000" -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    }
    
    $processes8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($processes8000) {
        $processes8000 | ForEach-Object {
            $processId = $_.OwningProcess
            Write-Host "Stopping process $processId on port 8000" -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
    }
} catch {
    Write-Host "Could not check for existing processes" -ForegroundColor Yellow
}

# Start Backend Server
Write-Host ""
Write-Host "[1/2] Starting Backend Server (FastAPI on port 8000)..." -ForegroundColor Green
$backendPath = Join-Path $PSScriptRoot "backend"
if (Test-Path $backendPath) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
    Write-Host "✓ Backend server starting in new window..." -ForegroundColor Green
} else {
    Write-Host "✗ Backend directory not found: $backendPath" -ForegroundColor Red
    exit 1
}

# Wait for backend to initialize
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend Server  
Write-Host ""
Write-Host "[2/2] Starting Frontend Server (Next.js on port 3000)..." -ForegroundColor Green
$frontendPath = Join-Path $PSScriptRoot "web"
if (Test-Path $frontendPath) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal
    Write-Host "✓ Frontend server starting in new window..." -ForegroundColor Green
} else {
    Write-Host "✗ Frontend directory not found: $frontendPath" -ForegroundColor Red
    exit 1
}

# Final instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Servers are starting up..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Blue
Write-Host "API Docs:    " -NoNewline -ForegroundColor White  
Write-Host "http://localhost:8000/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "Frontend App:" -NoNewline -ForegroundColor White
Write-Host "http://localhost:3000" -ForegroundColor Blue
Write-Host ""
Write-Host "Wait 10-15 seconds for both servers to fully start," -ForegroundColor Yellow
Write-Host "then visit: " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:3000" -ForegroundColor Blue -BackgroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")