Write-Host "Starting AI ERP SaaS Application..." -ForegroundColor Green

Write-Host ""
Write-Host "Step 1: Killing any process on port 3000..." -ForegroundColor Yellow
try {
    $processes = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
    if ($processes) {
        foreach ($processId in $processes) {
            Write-Host "Killing process $processId on port 3000" -ForegroundColor Red
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host "No processes found on port 3000" -ForegroundColor Green
    }
} catch {
    Write-Host "Could not check port 3000 processes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Starting the application on port 3000..." -ForegroundColor Yellow
Set-Location web
$env:PORT = "3000"
npm run dev

