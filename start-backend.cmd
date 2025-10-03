@echo off
echo Starting AI ERP Backend Server...
cd backend
REM Force local SQLite for dev runs outside Docker
set DATABASE_URL=sqlite:///./data/app.db
if not exist data mkdir data
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

