@echo off
echo ========================================
echo    AI ERP SaaS Application Launcher
echo ========================================
echo.
echo Starting both Frontend and Backend servers...
echo.

REM Start backend server in new window
echo [1/2] Starting Backend Server (FastAPI)...
start "AI ERP Backend" cmd /k "cd /d \"%~dp0backend\" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in new window  
echo [2/2] Starting Frontend Server (Next.js)...
start "AI ERP Frontend" cmd /k "cd /d \"%~dp0web\" && npm run dev"

echo.
echo ========================================
echo   Servers are starting up...
echo ========================================
echo.
echo Backend API will be available at: http://localhost:8000
echo Frontend App will be available at: http://localhost:3000
echo.
echo Wait 10-15 seconds, then visit: http://localhost:3000
echo.
echo Press any key to close this launcher...
pause >nul