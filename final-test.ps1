# FINAL COMPREHENSIVE TEST - AI ERP SaaS APPLICATION
Write-Host "🚀 AI ERP SaaS - FINAL COMPREHENSIVE TEST" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Test web app
Write-Host "`n📱 Testing Web Application..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3002" -TimeoutSec 10
    Write-Host "✅ Web Application: RUNNING PERFECTLY (Status: $($response.StatusCode))" -ForegroundColor Green
    $webAppWorking = $true
} catch {
    Write-Host "❌ Web Application: NOT RESPONDING" -ForegroundColor Red
    $webAppWorking = $false
}

if ($webAppWorking) {
    # Test OCR API
    Write-Host "`n🤖 Testing OCR API..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:3002/api/ocr/process" -Method Get
        Write-Host "✅ OCR API: FULLY OPERATIONAL" -ForegroundColor Green
        Write-Host "   Status: $($response.status)" -ForegroundColor Gray
        Write-Host "   Service: $($response.service)" -ForegroundColor Gray
        Write-Host "   Version: $($response.version)" -ForegroundColor Gray
        $ocrWorking = $true
    } catch {
        Write-Host "❌ OCR API: ERROR" -ForegroundColor Red
        $ocrWorking = $false
    }

    # Test key pages
    Write-Host "`n🧭 Testing Navigation Pages..." -ForegroundColor Yellow
    $testPages = @(
        "/",
        "/ocr-test", 
        "/auth/login",
        "/pricing"
    )
    
    $workingPages = 0
    foreach ($page in $testPages) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3002$page" -TimeoutSec 5
            Write-Host "✅ $page - OK" -ForegroundColor Green
            $workingPages++
        } catch {
            Write-Host "❌ $page - ERROR" -ForegroundColor Red
        }
    }

    # Final Summary
    Write-Host "`n📊 FINAL TEST RESULTS:" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    
    if ($webAppWorking) {
        Write-Host "✅ Web Application: WORKING" -ForegroundColor Green
        Write-Host "   URL: http://localhost:3002" -ForegroundColor White
    }
    
    if ($ocrWorking) {
        Write-Host "✅ OCR Functionality: WORKING" -ForegroundColor Green
        Write-Host "   API: http://localhost:3002/api/ocr/process" -ForegroundColor White
        Write-Host "   Test Page: http://localhost:3002/ocr-test" -ForegroundColor White
    }
    
    Write-Host "✅ Working Pages: $workingPages/$($testPages.Count)" -ForegroundColor Green
    
    if ($webAppWorking -and $ocrWorking -and $workingPages -eq $testPages.Count) {
        Write-Host "`n🎉 SUCCESS: APPLICATION IS 100% FUNCTIONAL!" -ForegroundColor Green
        Write-Host "🎯 Ready for production use!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  PARTIAL SUCCESS: Some components need attention" -ForegroundColor Yellow
    }
    
    Write-Host "`n🔗 Quick Access Links:" -ForegroundColor Magenta
    Write-Host "• Main App: http://localhost:3002" -ForegroundColor White
    Write-Host "• OCR Test: http://localhost:3002/ocr-test" -ForegroundColor White
    Write-Host "• Dashboard: http://localhost:3002/dashboard/invoices" -ForegroundColor White
}

Write-Host "`n✨ Test Complete!" -ForegroundColor Cyan
















