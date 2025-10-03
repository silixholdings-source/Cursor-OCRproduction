@echo off
title AI ERP SaaS - Working Start
color 0A
cls

echo.
echo ==========================================
echo     AI ERP SaaS - WORKING START
echo     This WILL work!
echo ==========================================
echo.

echo Starting Backend...
cd backend
start "Backend" cmd /c "python bulletproof_backend.py & pause"

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo Starting Frontend...
cd ..\web
start "Frontend" cmd /c "npm run dev & pause"

echo.
echo ==========================================
echo        SERVICES STARTING!
echo ==========================================
echo.
echo Backend will start in: backend window
echo Frontend will start in: frontend window
echo.
echo Wait for both to fully load, then:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo.
echo Press any key to close this window...
pause >nul
