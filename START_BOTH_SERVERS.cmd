@echo off
title AI ERP SaaS - Application Launcher
color 0E

echo.
echo ==========================================
echo     AI ERP SaaS - Application Launcher
echo ==========================================
echo.
echo This will start both backend and frontend servers
echo in separate windows for optimal development.
echo.
echo Please wait while servers initialize...
echo.

REM Start backend server in new window
echo [1/2] Starting Backend Server (FastAPI)...
start "AI ERP Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend server in new window
echo [2/2] Starting Frontend Server (Next.js)...
start "AI ERP Frontend" cmd /k "cd web && npm run dev"

echo.
echo ==========================================
echo   Both servers are starting up!
echo ==========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend:    http://localhost:3000
echo API Docs:    http://localhost:8000/docs
echo.
echo Wait 10-15 seconds for both servers to fully start,
echo then visit: http://localhost:3000
echo.
echo Press any key to close this launcher...
pause >nul

