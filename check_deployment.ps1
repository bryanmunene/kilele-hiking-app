# Quick Deployment Checker
Write-Host "🚀 Kilele Deployment Status Checker" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Check Git status
Write-Host "📦 Checking Git Status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $commit = Read-Host "Commit and push these changes? (y/n)"
    if ($commit -eq 'y') {
        git add .
        $message = Read-Host "Enter commit message"
        git commit -m $message
        git push origin main
        Write-Host "✅ Changes pushed to GitHub" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Git is clean, all changes committed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "📋 DEPLOYMENT CHECKLIST" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

Write-Host "Backend Deployment (Railway):" -ForegroundColor Yellow
Write-Host "  1. Go to https://railway.app" -ForegroundColor White
Write-Host "  2. Login with GitHub" -ForegroundColor White
Write-Host "  3. New Project → Deploy from GitHub" -ForegroundColor White
Write-Host "  4. Select: bryanmunene/kilele-hiking-app" -ForegroundColor White
Write-Host "  5. Set root directory to: backend" -ForegroundColor White
Write-Host "  6. Add environment variables (see DEPLOY_NOW.md)" -ForegroundColor White
Write-Host "  7. Generate domain" -ForegroundColor White
Write-Host ""

$backendUrl = Read-Host "Enter your Railway backend URL (or press Enter to skip)"

if ($backendUrl) {
    Write-Host ""
    Write-Host "✅ Backend URL saved: $backendUrl" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Frontend Deployment (Streamlit Cloud):" -ForegroundColor Yellow
Write-Host "  1. Go to https://share.streamlit.io" -ForegroundColor White
Write-Host "  2. Login with GitHub" -ForegroundColor White
Write-Host "  3. New app" -ForegroundColor White
Write-Host "  4. Repository: bryanmunene/kilele-hiking-app" -ForegroundColor White
Write-Host "  5. Branch: main" -ForegroundColor White
Write-Host "  6. Main file: frontend/Home.py" -ForegroundColor White
Write-Host "  7. Deploy!" -ForegroundColor White
Write-Host ""

$frontendUrl = Read-Host "Enter your Streamlit app URL (or press Enter to skip)"

if ($frontendUrl) {
    Write-Host ""
    Write-Host "✅ Frontend URL saved: $frontendUrl" -ForegroundColor Green
    Write-Host ""
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "🎉 DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

if ($backendUrl) {
    Write-Host "Backend:  $backendUrl" -ForegroundColor Green
} else {
    Write-Host "Backend:  Not deployed yet" -ForegroundColor Yellow
}

if ($frontendUrl) {
    Write-Host "Frontend: $frontendUrl" -ForegroundColor Green
} else {
    Write-Host "Frontend: Not deployed yet" -ForegroundColor Yellow
}

Write-Host ""

if ($backendUrl -and $frontendUrl) {
    Write-Host "🎉 Both services deployed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the app at: $frontendUrl" -ForegroundColor White
    Write-Host "  2. Create a test account" -ForegroundColor White
    Write-Host "  3. Try downloading a trail for offline" -ForegroundColor White
    Write-Host "  4. Test on your mobile phone" -ForegroundColor White
    Write-Host "  5. Share with friends for Saturday!" -ForegroundColor White
    Write-Host ""
    Write-Host "📱 Share this URL with users: $frontendUrl" -ForegroundColor Cyan
} else {
    Write-Host "⏳ Continue deployment and run this script again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📖 Full instructions in: DEPLOY_NOW.md" -ForegroundColor White
Write-Host ""
