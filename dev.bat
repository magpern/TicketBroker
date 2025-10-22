@echo off
REM Development runner script (Windows)

REM Check if virtual environment exists
if not exist venv (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set development environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Run the application
echo 🚀 Starting Flask application in development mode...
python run.py

pause
