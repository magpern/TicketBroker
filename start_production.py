#!/usr/bin/env python3
"""
Production startup script for TicketBroker
Uses Gunicorn WSGI server instead of Flask development server
"""

import os
import sys
import subprocess
from pathlib import Path

def start_production():
    """Start the application in production mode with Gunicorn"""
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'run.py'
    os.environ['FLASK_ENV'] = 'production'
    
    # Ensure logs directory exists
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Check if Gunicorn is installed
    try:
        import gunicorn
        print(f"✓ Gunicorn {gunicorn.__version__} found")
    except ImportError:
        print("✗ Gunicorn not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'], check=True)
        print("✓ Gunicorn installed")
    
    # Start Gunicorn server
    print("🚀 Starting TicketBroker in production mode...")
    print("📊 Server: Gunicorn WSGI")
    print("🌐 URL: http://localhost:5001")
    print("📝 Logs: logs/access.log, logs/error.log")
    print("⏹️  Stop: Ctrl+C")
    print("-" * 50)
    
    try:
        # Use Gunicorn configuration file
        cmd = [
            'gunicorn',
            '-c', 'gunicorn.conf.py',
            'run:app'
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error starting server: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = start_production()
    sys.exit(0 if success else 1)
