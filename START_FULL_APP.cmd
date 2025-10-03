@echo off
setlocal
title AI ERP SaaS - Full Application Startup
color 0A
cls

echo.
echo ==========================================
echo     AI ERP SaaS - Full Application
echo     Starting Frontend + Backend
echo ==========================================
echo.

REM Kill existing processes
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :3000 ^| findstr LISTENING') do (
    echo Stopping frontend process %%a...
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping backend process %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo ✅ Cleanup complete
echo.

REM Start Backend
echo 🚀 Starting Backend API Server...
cd backend
start "Backend API" cmd /k "title Backend API - Port 8000 && color 0B && echo Starting backend on port 8000... && python working_backend.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Frontend
echo 🌐 Starting Frontend Web App...
cd ..\web
start "Frontend Web" cmd /k "title Frontend Web - Port 3000 && color 0E && echo Starting frontend on port 3000... && npm run dev"

echo ⏳ Waiting for frontend to start...
timeout /t 8 /nobreak >nul

echo.
echo ==========================================
echo        ✅ APPLICATION STARTED! ✅
echo ==========================================
echo.
echo 🌐 Frontend URL: http://localhost:3000
echo 🔗 Backend URL:  http://localhost:8000
echo 📋 API Endpoints:
echo    GET  /health - Health check
echo    POST /api/v1/processing/demo - Demo OCR processing
echo    POST /api/v1/processing/process - File upload OCR
echo    GET  /api/v1/invoices - List invoices
echo.
echo 🧪 OCR Testing URLs:
echo    http://localhost:3000/ocr-test
echo    http://localhost:3000/test-ocr
echo    http://localhost:3000/demo
echo.
echo ⏰ Wait 10-15 seconds for full startup
echo.
echo Press any key to close this window...
pause >nul
