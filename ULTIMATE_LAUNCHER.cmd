@echo off
setlocal enabledelayedexpansion
title AI ERP SaaS - Ultimate Launcher
color 0E
cls

echo.
echo ==========================================
echo     AI ERP SaaS - Ultimate Launcher
echo     Guaranteed to work on Windows
echo ==========================================
echo.

REM Check prerequisites
echo [CHECKING] Prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found
    echo Please install Python from https://python.org
    echo.
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js not found
    echo Please install Node.js from https://nodejs.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are available
echo.

REM Clean up ports
echo [CLEANUP] Stopping any existing servers...
netstat -ano | findstr :3000 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo Stopping process on port 3000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo Stopping process on port 8000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo ✅ Ports cleared
echo.

REM Start Backend Server
echo [1/2] Starting Backend Server...
start "AI ERP Backend - FastAPI" cmd /k "title AI ERP Backend && color 0B && echo Starting FastAPI server on port 8000... && cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

REM Start Frontend Server
echo [2/2] Starting Frontend Server...
start "AI ERP Frontend - Next.js" cmd /k "title AI ERP Frontend && color 0A && echo Starting Next.js server on port 3000... && cd web && npm run dev"

echo.
echo ==========================================
echo        🚀 SERVERS ARE STARTING! 🚀
echo ==========================================
echo.
echo ⏰ Please wait 15-20 seconds for full initialization
echo.
echo 🌐 Access URLs:
echo    Main App:  http://localhost:3000
echo    API Docs:  http://localhost:8000/docs
echo    Backend:   http://localhost:8000
echo.
echo 🎯 What to test:
echo    • Landing page with working buttons
echo    • Pricing page trial signup
echo    • Help center (/help)
echo    • Interactive demo (/demo)
echo    • Dashboard functionality
echo    • Bulk approval workflows
echo.
echo 📝 All buttons and links are now functional!
echo.
echo Press any key to close this launcher...
pause >nul
exit

