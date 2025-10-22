#!/bin/bash
# Development runner script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Set development environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run the application
echo "🚀 Starting Flask application in development mode..."
python run.py
