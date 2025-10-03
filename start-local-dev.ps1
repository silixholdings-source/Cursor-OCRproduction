# Start Local Development Environment
# This script starts both frontend and backend for local development

Write-Host "🚀 Starting AI ERP SaaS Application for Local Development" -ForegroundColor Green

# Set environment variables for local development
$env:DATABASE_URL = "sqlite:///./backend/data/app.db"
$env:REDIS_URL = ""
$env:ENVIRONMENT = "development"
$env:DEBUG = "true"
$env:SECRET_KEY = "dev-secret-key-for-local-development-only"
$env:JWT_SECRET = "dev-jwt-secret-for-local-development-only"
$env:BACKEND_CORS_ORIGINS = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000"
$env:ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:OCR_PROVIDER = "advanced"

Write-Host "📦 Environment variables set for local development" -ForegroundColor Yellow

# Start backend
Write-Host "🔧 Starting Backend Server..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-Command", "cd backend; python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "🌐 Starting Frontend Server..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-Command", "cd web; npm run dev" -WindowStyle Normal

Write-Host "✅ Both servers are starting up!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3000 (or 3001/3002 if 3000 is busy)" -ForegroundColor Cyan
Write-Host "🔧 Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n🎯 OCR Functionality is ready for testing!" -ForegroundColor Green
Write-Host "Upload an invoice to test the world-class OCR system" -ForegroundColor Yellow
