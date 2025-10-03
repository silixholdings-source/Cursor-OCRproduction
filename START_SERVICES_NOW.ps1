# START SERVICES NOW - PowerShell Script
# This will start both backend and frontend services

Write-Host "Starting AI ERP SaaS Services..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Kill any existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force

# Start Backend
Write-Host "Starting Backend on port 8000..." -ForegroundColor Cyan
Set-Location "backend"
Start-Process -FilePath "python" -ArgumentList "bulletproof_backend.py" -WindowStyle Normal

# Wait a moment
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "Starting Frontend on port 3000..." -ForegroundColor Cyan
Set-Location "..\web"
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Normal

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
Write-Host "Checking service status..." -ForegroundColor Cyan

$backendRunning = $false
$frontendRunning = $false

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "✅ Backend is running on http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend is not responding" -ForegroundColor Red
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        $frontendRunning = $true
        Write-Host "✅ Frontend is running on http://localhost:3000" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend is not responding" -ForegroundColor Red
}

Write-Host "=================================" -ForegroundColor Green
if ($backendRunning -and $frontendRunning) {
    Write-Host "🎉 ALL SERVICES ARE RUNNING!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "OCR Test: http://localhost:3000/ocr-test" -ForegroundColor White
} else {
    Write-Host "⚠️  Some services may not be running properly" -ForegroundColor Yellow
    Write-Host "Check the separate windows that opened for each service" -ForegroundColor Yellow
}

Write-Host "=================================" -ForegroundColor Green
Write-Host "Press any key to close this window..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
