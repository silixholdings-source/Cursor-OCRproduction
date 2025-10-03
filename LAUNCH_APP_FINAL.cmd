@echo off
title AI ERP SaaS - Application Launcher
color 0E
cls

echo.
echo ==========================================
echo     AI ERP SaaS - Application Launcher
echo ==========================================
echo.
echo Starting your world-class AI ERP platform...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again.
    pause
    exit /b 1
)

echo Prerequisites check: PASSED
echo.

REM Kill any existing processes on our ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    echo Stopping process on port 3000...
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process on port 8000...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo [1/2] Starting Backend Server...
start "AI ERP Backend" /min cmd /k "title AI ERP Backend && color 0B && cd backend && echo Starting FastAPI server... && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to initialize...
timeout /t 6 /nobreak >nul

echo [2/2] Starting Frontend Server...
start "AI ERP Frontend" /min cmd /k "title AI ERP Frontend && color 0A && cd web && echo Starting Next.js server... && npm run dev"

echo.
echo ==========================================
echo        🚀 SERVERS STARTING UP! 🚀
echo ==========================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/docs
echo Frontend App: http://localhost:3000
echo.
echo ⏰ Please wait 15-20 seconds for both servers
echo    to fully initialize, then visit:
echo.
echo    👉 http://localhost:3000 👈
echo.
echo 🎉 Your AI ERP SaaS application will be ready!
echo.
echo Press any key to close this launcher...
pause >nul
exit

