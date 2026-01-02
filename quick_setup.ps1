# Quick Start Script for Development
# This temporarily uses SQLite instead of PostgreSQL for easy setup

Write-Host "Setting up Multi-Tenant School Management System..." -ForegroundColor Green

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Temporarily switch to SQLite for development
Write-Host "`nSwitching to SQLite for easy setup..." -ForegroundColor Yellow
$settingsPath = "school_management\settings.py"
$content = Get-Content $settingsPath -Raw

# Comment out PostgreSQL and uncomment SQLite
if ($content -match "django.db.backends.postgresql") {
    $content = $content -replace "DATABASES = \{[^}]*'ENGINE': 'django.db.backends.postgresql',[^}]*\}", @"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# PostgreSQL config commented for development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='school_management'),
#         'USER': config('DB_USER', default='postgres'),
#         'PASSWORD': config('DB_PASSWORD', default=''),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }
"@
    Set-Content $settingsPath $content
    Write-Host "✓ Switched to SQLite" -ForegroundColor Green
}

# Create migrations
Write-Host "`nCreating database migrations..." -ForegroundColor Yellow
python manage.py makemigrations

# Run migrations
Write-Host "`nRunning migrations..." -ForegroundColor Yellow
python manage.py migrate

# Initialize Super Admin
Write-Host "`nInitializing Super Admin..." -ForegroundColor Yellow
python manage.py init_superadmin

Write-Host "`n✓ Setup Complete!" -ForegroundColor Green
Write-Host "`nSuper Admin Credentials:" -ForegroundColor Cyan
Write-Host "  Email: superadmin@sms.com" -ForegroundColor White
Write-Host "  Password: SuperAdmin@2025" -ForegroundColor White

Write-Host "`nTo start the server, run:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White

Write-Host "`nAPI will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000/api/" -ForegroundColor White

Write-Host "`nTo switch back to PostgreSQL:" -ForegroundColor Yellow
Write-Host "  1. Install and configure PostgreSQL" -ForegroundColor White
Write-Host "  2. Uncomment PostgreSQL config in settings.py" -ForegroundColor White
Write-Host "  3. Comment out SQLite config" -ForegroundColor White
Write-Host "  4. Run migrations again" -ForegroundColor White
