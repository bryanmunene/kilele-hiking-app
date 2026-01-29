# Production Package Installation Script
# Run this to install all production dependencies

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  Kilele Production Dependencies Installation" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Install backend dependencies
Write-Host ""
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "backend"
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Backend installation failed" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host ""
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "..\frontend"
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend installation failed" -ForegroundColor Red
    exit 1
}

# Return to project root
Set-Location ".."

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "  ✅ All dependencies installed successfully!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy .env.example to .env" -ForegroundColor White
Write-Host "  2. Add your production credentials" -ForegroundColor White
Write-Host "  3. Test locally before deploying" -ForegroundColor White
Write-Host ""
Write-Host "📚 Read QUICKSTART_V2.md for deployment guide" -ForegroundColor Yellow
