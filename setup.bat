@echo off
REM Setup script for TicketBroker Flask application (Windows)

echo 🎫 Setting up TicketBroker Flask Application...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo 🐍 Found Python %python_version%

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing Python packages...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist data mkdir data
if not exist app\static\images mkdir app\static\images
if not exist logs mkdir logs

REM Copy environment file if it doesn't exist
if not exist .env (
    echo 📋 Creating .env file from template...
    copy env.example .env
    echo ⚠️  Please edit .env file with your actual settings before running the application
)

REM Create a sample class photo placeholder
if not exist app\static\images\class-photo.jpg (
    echo 🖼️ Creating placeholder for class photo...
    echo Please add your class photo as app/static/images/class-photo.jpg > app\static\images\class-photo.jpg
)

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo    1. Activate virtual environment: venv\Scripts\activate.bat
echo    2. Edit .env file with your settings
echo    3. Add your class photo to app/static/images/class-photo.jpg
echo    4. Run: python run.py
echo.
echo 🔧 For VS Code debugging:
echo    - Select 'Flask App Debug' configuration
echo    - Press F5 to start debugging
echo.
echo 🐳 For Docker deployment:
echo    - Run: docker-compose up -d

pause
