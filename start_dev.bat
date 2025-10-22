@echo off
REM Development startup script for Windows
REM Starts TicketBroker with Flask development server (warning suppressed)

echo Starting TicketBroker in development mode...
echo.

REM Activate virtual environment
call venv_new\Scripts\activate

REM Start Flask development server
python run.py

pause
