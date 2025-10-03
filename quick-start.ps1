# Quick start commands for AI ERP SaaS
Write-Host "AI ERP SaaS - Quick Start Commands" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the backend server:" -ForegroundColor Yellow
Write-Host "cd backend" -ForegroundColor White
Write-Host "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "To start the frontend server (in a new terminal):" -ForegroundColor Yellow  
Write-Host "cd web" -ForegroundColor White
Write-Host "npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Or run the automated launcher:" -ForegroundColor Cyan
Write-Host ".\start-servers.ps1" -ForegroundColor White
Write-Host ""

