#!/bin/bash
# Setup script for TicketBroker Flask application

echo "🎫 Setting up TicketBroker Flask Application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Found Python $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p app/static/images
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual settings before running the application"
fi

# Create a sample class photo placeholder
if [ ! -f app/static/images/class-photo.jpg ]; then
    echo "🖼️ Creating placeholder for class photo..."
    echo "Please add your class photo as app/static/images/class-photo.jpg" > app/static/images/class-photo.jpg
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Edit .env file with your settings"
echo "   3. Add your class photo to app/static/images/class-photo.jpg"
echo "   4. Run: python run.py"
echo ""
echo "🔧 For VS Code debugging:"
echo "   - Select 'Flask App Debug' configuration"
echo "   - Press F5 to start debugging"
echo ""
echo "🐳 For Docker deployment:"
echo "   - Run: docker-compose up -d"
