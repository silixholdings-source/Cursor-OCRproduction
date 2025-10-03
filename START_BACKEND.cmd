@echo off
title AI ERP Backend Server
color 0B

echo.
echo ==========================================
echo     AI ERP SaaS - Backend Server
echo ==========================================
echo.
echo Starting FastAPI server on port 8000...
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Backend server stopped.
pause

