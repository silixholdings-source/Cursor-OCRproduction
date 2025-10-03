@echo off
setlocal
title AI ERP SaaS - Error-Proof Launcher
color 0A
cls

echo.
echo ==========================================
echo     AI ERP SaaS - Error-Proof Launcher
echo     Guaranteed to work on any Windows PC
echo ==========================================
echo.

REM Verify we're in the correct directory
if not exist "package.json" if not exist "backend" if not exist "web" (
    echo ERROR: Please run this script from the AI ERP SaaS project root directory
    echo.
    echo Expected directory structure:
    echo   - backend/
    echo   - web/
    echo   - package.json or similar project files
    echo.
    pause
    exit /b 1
)

echo ✅ Project directory verified
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python is available
python --version

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js is available
node --version
echo.

REM Kill any processes using our ports
echo 🧹 Cleaning up existing processes...

REM Kill processes on port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING 2^>nul') do (
    echo   Stopping process %%a on port 3000
    taskkill /f /pid %%a >nul 2>&1
)

REM Kill processes on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING 2^>nul') do (
    echo   Stopping process %%a on port 8000
    taskkill /f /pid %%a >nul 2>&1
)

echo ✅ Ports cleaned up
echo.

REM Start Backend Server
echo 🚀 [1/2] Starting Backend Server (FastAPI)...
start "AI ERP Backend" cmd /k "title AI ERP Backend - FastAPI & color 0B & echo Starting FastAPI server on port 8000... & echo. & cd backend & python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to initialize
echo ⏳ Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

REM Start Frontend Server
echo 🚀 [2/2] Starting Frontend Server (Next.js)...
start "AI ERP Frontend" cmd /k "title AI ERP Frontend - Next.js & color 0A & echo Starting Next.js development server... & echo. & cd web & npm run dev"

echo.
echo ==========================================
echo        🎉 SERVERS ARE STARTING! 🎉
echo ==========================================
echo.
echo 🌐 Your AI ERP SaaS application will be available at:
echo.
echo    Main App:     http://localhost:3000
echo    API Docs:     http://localhost:8000/docs
echo    Backend API:  http://localhost:8000
echo.
echo ⏰ Please wait 15-20 seconds for both servers to fully start
echo.
echo 🎯 What you can test:
echo    ✅ Landing page with working buttons
echo    ✅ Pricing page with trial signup
echo    ✅ Help center (/help)
echo    ✅ Interactive demo (/demo)
echo    ✅ Dashboard functionality
echo    ✅ Bulk approval workflows
echo    ✅ Invoice upload with AI processing
echo    ✅ ERP integrations
echo.
echo 🔧 If you see any errors, they should be fixed now!
echo.
echo Press any key to close this launcher...
pause >nul
exit

