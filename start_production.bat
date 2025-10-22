@echo off
REM Production startup script for Windows
REM Starts TicketBroker with Gunicorn WSGI server

echo Starting TicketBroker in production mode...
echo.

REM Activate virtual environment
call venv_new\Scripts\activate

REM Set environment variables
set FLASK_APP=run.py
set FLASK_ENV=production

REM Start Gunicorn
gunicorn -c gunicorn.conf.py run:app

pause
