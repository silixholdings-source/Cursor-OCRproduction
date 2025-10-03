@echo off
setlocal
title OCR Backend - Working Version
color 0A
cls

echo.
echo ==========================================
echo     OCR Backend - Working Version
echo     Starting backend for OCR testing
echo ==========================================
echo.

REM Kill existing processes on port 8000
echo 🧹 Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process %%a on port 8000...
    taskkill /f /pid %%a >nul 2>&1
)

echo ✅ Cleanup complete
echo.

REM Start simple backend
echo 🚀 Starting Simple OCR Backend...
cd backend
start "OCR Backend" cmd /k "title OCR Backend - Port 8000 && color 0B && echo Starting backend on port 8000... && python simple_backend.py"

echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak >nul

echo.
echo ==========================================
echo        ✅ BACKEND STARTED! ✅
echo ==========================================
echo.
echo 🌐 Backend URL: http://localhost:8000
echo 📋 Available endpoints:
echo    GET  /health - Health check
echo    POST /api/v1/processing/demo - Demo OCR processing
echo    POST /api/v1/processing/process - File upload OCR
echo    GET  /api/v1/ocr/status - OCR service status
echo.
echo 🧪 To test the backend, run:
echo    python test-backend-simple.py
echo.
echo ⏰ Wait 10-15 seconds for full startup
echo.
echo Press any key to close this window...
pause >nul
