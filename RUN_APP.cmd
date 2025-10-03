@echo off
title AI ERP SaaS - Reliable Launcher
color 0F
cls

echo.
echo ==========================================
echo     AI ERP SaaS - Reliable App Launcher
echo ==========================================
echo.

REM Check if in correct directory
if not exist "backend\main.py" (
    echo ERROR: Cannot find backend\main.py
    echo Please make sure you're in the AI ERP SaaS project directory
    pause
    exit /b 1
)

if not exist "web\package.json" (
    echo ERROR: Cannot find web\package.json
    echo Please make sure you're in the AI ERP SaaS project directory
    pause
    exit /b 1
)

echo ✅ Project files found
echo.

REM Start Backend
echo [1/2] Starting Backend Server...
cd backend
start "AI ERP Backend" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
cd ..

REM Wait
echo Waiting for backend to start...
ping 127.0.0.1 -n 6 > nul

REM Start Frontend  
echo [2/2] Starting Frontend Server...
cd web
start "AI ERP Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================
echo        🚀 SERVERS STARTING! 🚀
echo ==========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Wait 15 seconds, then visit:
echo http://localhost:3000
echo.
echo All buttons and links are now working!
echo.
pause

