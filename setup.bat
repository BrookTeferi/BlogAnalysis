@echo off
echo ========================================
echo Django Analytics API - Quick Setup
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)
echo.

echo Step 3: Generating sample data...
python manage.py generate_sample_data
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate sample data
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now:
echo   1. Run the server: python manage.py runserver
echo   2. Create admin user: python manage.py createsuperuser
echo.
echo Test the APIs at:
echo   - http://127.0.0.1:8000/analytics/blog-views/?object_type=country^&range=month
echo   - http://127.0.0.1:8000/analytics/top/?top=user^&range=year
echo   - http://127.0.0.1:8000/analytics/performance/?compare=month
echo.
pause
