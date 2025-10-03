@echo off
echo ============================================
echo     AI ERP SaaS Application Launcher
echo ============================================
echo.
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd web && npm run dev"

echo.
echo ============================================
echo   Both servers are starting up!
echo ============================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Wait 10-15 seconds, then visit:
echo http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul

