@echo off
title AI ERP SaaS - Quick Start
color 0A

echo.
echo ========================================
echo     AI ERP SaaS - Quick Start
echo ========================================
echo.

echo 🚀 Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python simple_main.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 8 /nobreak >nul

echo.
echo 🌐 Starting Frontend Server...
start "Frontend Server" cmd /k "cd web && npm run dev"

echo.
echo ✅ Both services starting!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo Press any key to exit this launcher...
pause >nul

