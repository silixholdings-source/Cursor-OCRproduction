@echo off
cls
echo.
echo ==========================================
echo     AI ERP SaaS - Simple Launcher
echo ==========================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ERROR: Please run this from the project root directory
    echo Expected to find 'backend' folder
    pause
    exit /b 1
)

if not exist "web" (
    echo ERROR: Please run this from the project root directory  
    echo Expected to find 'web' folder
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Backend" cmd /k "cd backend & python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "Frontend" cmd /k "cd web & npm run dev"

echo.
echo ==========================================
echo   Servers are starting!
echo ==========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Wait 15 seconds, then visit: http://localhost:3000
echo.
pause