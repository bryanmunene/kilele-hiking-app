# Kilele Strava Integration Setup Script
# This script will guide you through setting up Strava API integration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Kilele Strava Integration Setup   " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
$envPath = "backend\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "Error: backend\.env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Get Strava API Credentials" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use Strava integration, you need to create a Strava API application." -ForegroundColor White
Write-Host ""
Write-Host "I will open the Strava API settings page for you now..." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to open Strava API settings in your browser"

# Open Strava API page
Start-Process "https://www.strava.com/settings/api"

Write-Host ""
Write-Host "Follow these steps on the Strava website:" -ForegroundColor Cyan
Write-Host "1. Log in with your Strava account" -ForegroundColor White
Write-Host "2. If you don't have an app yet, click 'Create An App'" -ForegroundColor White
Write-Host "3. Fill in the form:" -ForegroundColor White
Write-Host "   - Application Name: Kilele Hiking App" -ForegroundColor Gray
Write-Host "   - Category: Training" -ForegroundColor Gray
Write-Host "   - Website: http://localhost:8501" -ForegroundColor Gray
Write-Host "   - Authorization Callback Domain: localhost" -ForegroundColor Gray
Write-Host "4. Click 'Create' or 'Update'" -ForegroundColor White
Write-Host "5. Copy your Client ID and Client Secret" -ForegroundColor White
Write-Host ""

# Prompt for credentials
Write-Host "Step 2: Enter Your Strava Credentials" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow
Write-Host ""

$clientId = Read-Host "Enter your Strava Client ID"
if ([string]::IsNullOrWhiteSpace($clientId)) {
    Write-Host "Error: Client ID cannot be empty!" -ForegroundColor Red
    exit 1
}

$clientSecret = Read-Host "Enter your Strava Client Secret"
if ([string]::IsNullOrWhiteSpace($clientSecret)) {
    Write-Host "Error: Client Secret cannot be empty!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Updating Configuration" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow

# Read existing .env content
$envContent = Get-Content $envPath -Raw

# Remove any existing Strava configuration
$envContent = $envContent -replace "(?m)^#?\s*STRAVA_CLIENT_ID=.*$", ""
$envContent = $envContent -replace "(?m)^#?\s*STRAVA_CLIENT_SECRET=.*$", ""
$envContent = $envContent -replace "(?m)^#?\s*STRAVA_REDIRECT_URI=.*$", ""
$envContent = $envContent -replace "(?m)^#?\s*STRAVA_WEBHOOK_VERIFY_TOKEN=.*$", ""
$envContent = $envContent -replace "(?m)^# Strava API Integration.*$", ""
$envContent = $envContent -replace "(?m)^# Get credentials from.*$", ""

# Clean up multiple newlines
$envContent = $envContent -replace "(\r?\n){3,}", "`n`n"

# Add Strava configuration
$stravaConfig = @"

# Strava API Integration
STRAVA_CLIENT_ID=$clientId
STRAVA_CLIENT_SECRET=$clientSecret
STRAVA_REDIRECT_URI=http://localhost:8501/strava/callback
STRAVA_WEBHOOK_VERIFY_TOKEN=kilele_strava_webhook_2026
"@

$envContent = $envContent.TrimEnd() + $stravaConfig

# Save updated .env file
Set-Content -Path $envPath -Value $envContent -NoNewline

Write-Host "✅ Configuration saved to backend\.env" -ForegroundColor Green
Write-Host ""

# Check if backend is running
Write-Host "Step 4: Restart Backend Server" -ForegroundColor Yellow
Write-Host "---------------------------------------" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Would you like to start the backend server now? (y/n)"

if ($choice -eq 'y' -or $choice -eq 'Y') {
    Write-Host ""
    Write-Host "Starting backend server..." -ForegroundColor Green
    Write-Host ""
    Write-Host "The backend will start at http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server when done" -ForegroundColor Gray
    Write-Host ""
    
    Start-Sleep -Seconds 2
    
    cd backend
    python main.py
} else {
    Write-Host ""
    Write-Host "Skipping backend startup." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To start the backend manually:" -ForegroundColor White
    Write-Host "  cd backend" -ForegroundColor Gray
    Write-Host "  python main.py" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Setup Complete! 🎉                " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Make sure backend is running (python main.py in backend folder)" -ForegroundColor Gray
Write-Host "2. Open Streamlit app: streamlit run frontend/Home.py" -ForegroundColor Gray
Write-Host "3. Go to Strava page (🟠 in sidebar)" -ForegroundColor Gray
Write-Host "4. Click 'Connect Strava' button" -ForegroundColor Gray
Write-Host "5. Authorize the app on Strava" -ForegroundColor Gray
Write-Host ""
Write-Host "Your Strava activities will now sync automatically! 🚀" -ForegroundColor Green
