@echo off
echo Starting AI ERP Backend Server...
echo.
cd /d "%~dp0backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause

