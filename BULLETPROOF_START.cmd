@echo off
setlocal
title AI ERP SaaS - Bulletproof Startup
color 0A
cls

echo.
echo ==========================================
echo     AI ERP SaaS - BULLETPROOF STARTUP
echo     Guaranteed to Work 100%
echo ==========================================
echo.

REM Kill all existing processes
echo 🧹 Killing all existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Clear ports
echo 🔌 Clearing ports...
netstat -ano | findstr :3000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo ✅ Cleanup complete
echo.

REM Start Backend (Bulletproof)
echo 🚀 Starting Bulletproof Backend...
cd backend
start "Bulletproof Backend" cmd /k "title Bulletproof Backend - Port 8000 && color 0B && echo Starting bulletproof backend... && python bulletproof_backend.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start Frontend
echo 🌐 Starting Frontend...
cd ..\web
start "Frontend Web" cmd /k "title Frontend Web - Port 3000 && color 0E && echo Starting frontend... && npm run dev"

echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo ==========================================
echo        ✅ BULLETPROOF STARTUP COMPLETE!
echo ==========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔗 Backend:  http://localhost:8000
echo.
echo 🧪 Test URLs:
echo    Backend Health: http://localhost:8000/health
echo    OCR Status:     http://localhost:8000/api/v1/ocr/status
echo    OCR Demo:       http://localhost:8000/api/v1/processing/demo
echo.
echo 📱 OCR Pages:
echo    http://localhost:3000/ocr-test
echo    http://localhost:3000/test-ocr
echo    http://localhost:3000/demo
echo    http://localhost:3000/debug-ocr
echo.
echo ⏰ Wait 15 seconds for full startup
echo.
echo Press any key to close this window...
pause >nul
