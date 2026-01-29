# Automated Backup Script for Production
# Run this as a cron job or scheduled task

# Windows Task Scheduler (PowerShell)
# Run daily at 2 AM
# Action: powershell.exe
# Arguments: -File "C:\path\to\Kilele Project\backend\backup_script.ps1"

Write-Host "🔄 Starting Kilele database backup..." -ForegroundColor Cyan

# Activate virtual environment
& ".venv\Scripts\Activate.ps1"

# Navigate to backend directory
Set-Location "C:\Users\BMK\Desktop\MEGA FOLDER\Kilele Project\backend"

# Run backup
python backup_service.py create

# Cleanup old backups (keep last 10)
python backup_service.py cleanup

Write-Host "✅ Backup complete!" -ForegroundColor Green

# Linux cron job alternative:
# Add to crontab (crontab -e):
# 0 2 * * * cd /path/to/Kilele\ Project/backend && python backup_service.py create && python backup_service.py cleanup
