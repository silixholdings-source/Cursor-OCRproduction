@echo off
setlocal
title OCR Testing - Simple Backend
color 0A
cls

echo.
echo ==========================================
echo     OCR Testing - Simple Backend
echo     Starting backend for OCR testing
echo ==========================================
echo.

REM Kill existing processes
echo 🧹 Cleaning up existing processes...
taskkill /f /im "uvicorn.exe" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo ✅ Cleanup complete
echo.

REM Start simple backend
echo 🚀 Starting Simple OCR Test Backend...
start "OCR Test Backend" cmd /k "title OCR Test Backend & color 0B & cd backend & echo Starting simple backend on port 8000... & python simple_backend.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

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
echo 🧪 To test OCR functionality, run:
echo    node test-ocr-complete.js
echo.
echo ⏰ Wait 5-10 seconds for full startup
echo.
pause
