# Restart Script for Kilele Hiking App
# Run this after stopping all servers

Write-Host "==================================" -ForegroundColor Green
Write-Host "  Kilele App Restart Script" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

# Step 1: Kill existing Python processes
Write-Host "Step 1: Stopping existing Python processes..." -ForegroundColor Yellow
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✓ Processes stopped" -ForegroundColor Green
Write-Host ""

# Step 2: Recreate database
Write-Host "Step 2: Recreating database..." -ForegroundColor Yellow
Set-Location "c:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project\backend"

if (Test-Path "kilele.db") {
    Remove-Item "kilele.db" -Force
    Write-Host "✓ Old database deleted" -ForegroundColor Green
}

& ".\venv\Scripts\python.exe" "seed_data.py"
Write-Host "✓ Database recreated with new tables" -ForegroundColor Green
Write-Host ""

# Step 3: Instructions for starting servers
Write-Host "Step 3: Start servers in SEPARATE terminals:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Cyan
Write-Host "  cd 'c:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project\backend'" -ForegroundColor White
Write-Host "  venv\Scripts\activate" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Cyan
Write-Host "  cd 'c:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project\frontend'" -ForegroundColor White
Write-Host "  streamlit run Home.py" -ForegroundColor White
Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Database ready! Start servers." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
