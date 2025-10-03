@echo off
title AI ERP SaaS - Enhanced Application Launcher
color 0A

echo.
echo =============================================
echo     AI ERP SaaS - Enhanced Application
echo =============================================
echo.
echo 🚀 Starting Enhanced Backend with AI Features...
start "Enhanced Backend" cmd /k "cd backend && python simple_main.py"

echo.
echo ⏳ Waiting for backend to initialize...
timeout /t 10 /nobreak >nul

echo.
echo 🌐 Starting Enhanced Frontend...
start "Enhanced Frontend" cmd /k "cd web && npm run dev"

echo.
echo ✅ Enhanced Application Starting!
echo.
echo 🎯 ENHANCED FEATURES INCLUDED:
echo   • Real-time WebSocket updates
echo   • AI-powered vendor matching
echo   • Advanced analytics dashboard
echo   • Bulk operations for invoices
echo   • Keyboard shortcuts (Ctrl+D, Ctrl+I, etc.)
echo   • Progressive Web App (PWA)
echo   • Enhanced search functionality
echo   • Fraud detection and OCR analysis
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8001
echo 📚 API Docs: http://localhost:8001/docs
echo 🔄 WebSocket: ws://localhost:8001/ws
echo.
echo 🎊 Your app now has WORLD-CLASS features!
echo.
echo Press any key to exit this launcher...
pause >nul
