@echo off
REM OurChat Production Readiness Test Runner (Simple Batch Version)
REM Run this file to test your application for production readiness

echo.
echo ============================================
echo   OurChat Production Readiness Tests
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.7+ first.
    pause
    exit /b 1
)

REM Check if the test script exists
if not exist "production_readiness_test.py" (
    echo ERROR: production_readiness_test.py not found.
    echo Please make sure you're running this from the correct directory.
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing/updating test dependencies...
pip install requests psutil Pillow Flask Flask-SQLAlchemy Werkzeug

REM Run the tests
echo.
echo Running production readiness tests...
echo Target: http://localhost:5000
echo.

python production_readiness_test.py --url http://localhost:5000 --verbose

REM Check results
if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   SUCCESS: Tests completed!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo   WARNING: Issues found that need attention
    echo ============================================
)

echo.
echo Check the generated HTML and text reports for details.
echo.
pause
