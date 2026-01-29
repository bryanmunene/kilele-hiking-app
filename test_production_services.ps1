# Test Production Services Script
# Verifies that production services are configured correctly

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  Kilele Production Services Test" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& ".venv\Scripts\Activate.ps1"
Set-Location "backend"

# Test database connection
Write-Host "🗄️  Testing database connection..." -ForegroundColor Yellow
python -c "from config import settings; from database import engine; engine.connect(); print('✅ Database connection successful')"

# Test Cloudinary
Write-Host ""
Write-Host "☁️  Testing Cloudinary..." -ForegroundColor Yellow
python -c "from config import settings; print('✅ Cloudinary configured') if settings.has_cloudinary else print('⚠️ Cloudinary not configured')"

# Test Email service
Write-Host ""
Write-Host "📧 Testing email service..." -ForegroundColor Yellow
python -c "from config import settings; print('✅ Email service configured') if settings.has_email else print('⚠️ Email service not configured')"

# Test Sentry
Write-Host ""
Write-Host "🔍 Testing Sentry..." -ForegroundColor Yellow
python -c "from config import settings; print('✅ Sentry configured') if settings.has_sentry else print('⚠️ Sentry not configured')"

# Show configuration summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  Configuration Summary" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
python -c @"
from config import settings
print(f'Environment: {settings.ENVIRONMENT}')
print(f'Database: {'PostgreSQL' if settings.use_postgresql else 'SQLite'}')
print(f'Cloudinary: {'✅' if settings.has_cloudinary else '❌'}')
print(f'Email: {'✅' if settings.has_email else '❌'}')
print(f'Sentry: {'✅' if settings.has_sentry else '❌'}')
print(f'Debug Mode: {settings.DEBUG}')
"@

Set-Location ".."
Write-Host ""
Write-Host "✅ Service test complete!" -ForegroundColor Green
