# AI ERP SaaS - Full Stack Startup Script
# This script will start all services needed for the complete application

Write-Host "🚀 Starting AI ERP SaaS Full Stack..." -ForegroundColor Green

# Check if Docker is running
Write-Host "📋 Checking Docker status..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
    $dockerRunning = $true
} catch {
    Write-Host "⚠️  Docker is not running. Starting services manually..." -ForegroundColor Yellow
    $dockerRunning = $false
}

if ($dockerRunning) {
    # Use Docker Compose
    Write-Host "🐳 Starting services with Docker Compose..." -ForegroundColor Blue
    
    # Fix deprecated version warning
    Write-Host "📝 Fixing docker-compose.yml version warning..." -ForegroundColor Yellow
    $dockerComposeContent = Get-Content "docker-compose.yml"
    $dockerComposeContent = $dockerComposeContent | Where-Object { $_ -notmatch "^version:" }
    $dockerComposeContent | Set-Content "docker-compose.yml"
    
    # Start all services
    docker-compose up --build -d
    
    Write-Host "🎉 All services started with Docker!" -ForegroundColor Green
    Write-Host "📊 Service URLs:" -ForegroundColor Cyan
    Write-Host "   - Web Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   - Database: localhost:5432" -ForegroundColor White
    Write-Host "   - Redis: localhost:6379" -ForegroundColor White
    
} else {
    # Manual setup
    Write-Host "🔧 Setting up services manually..." -ForegroundColor Blue
    
    # Check if backend virtual environment exists
    if (!(Test-Path "backend\venv")) {
        Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
        Set-Location backend
        python -m venv venv
        Set-Location ..
    }
    
    # Install backend dependencies
    Write-Host "📥 Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location backend
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Set-Location ..
    
    # Start backend server in background
    Write-Host "🔥 Starting backend server..." -ForegroundColor Blue
    Start-Process powershell -ArgumentList "-Command", "Set-Location backend; .\venv\Scripts\Activate.ps1; uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Minimized
    
    # Web frontend is already running, just confirm
    Write-Host "🌐 Web frontend should already be running on port 3000" -ForegroundColor Green
    
    Write-Host "⚠️  Note: Database and Redis are not available in manual mode" -ForegroundColor Yellow
    Write-Host "   The app will use SQLite fallback and in-memory caching" -ForegroundColor Yellow
    
    Write-Host "🎉 Manual setup complete!" -ForegroundColor Green
    Write-Host "📊 Service URLs:" -ForegroundColor Cyan
    Write-Host "   - Web Frontend: http://localhost:3000 ✅" -ForegroundColor White
    Write-Host "   - Backend API: http://localhost:8000 🔄 (starting...)" -ForegroundColor White
    Write-Host "   - API Docs: http://localhost:8000/docs 🔄 (starting...)" -ForegroundColor White
}

# Wait a moment for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test services
Write-Host "🧪 Testing service connectivity..." -ForegroundColor Blue

# Test web frontend
try {
    $webResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Web Frontend: Online (Status: $($webResponse.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Web Frontend: Offline" -ForegroundColor Red
}

# Test backend API
try {
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Backend API: Online (Status: $($apiResponse.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend API: Offline or starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:3000 to access the application" -ForegroundColor White
Write-Host "2. Test login with: demo@example.com / password" -ForegroundColor White
Write-Host "3. Try uploading an invoice to test OCR functionality" -ForegroundColor White
Write-Host "4. Check http://localhost:8000/docs for API documentation" -ForegroundColor White
Write-Host ""
Write-Host "🛠️  To stop all services:" -ForegroundColor Yellow
if ($dockerRunning) {
    Write-Host "   docker-compose down" -ForegroundColor White
} else {
    Write-Host "   Close the PowerShell windows or press Ctrl+C" -ForegroundColor White
}

Write-Host ""
Write-Host "🚀 AI ERP SaaS Full Stack is ready!" -ForegroundColor Green
