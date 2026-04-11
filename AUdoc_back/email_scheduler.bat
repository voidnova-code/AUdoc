@echo off
REM ============================================================================
REM AUdoc Email Scheduler - Windows Batch Script
REM ============================================================================
REM 
REM This script starts the email scheduler in the background.
REM
REM Usage:
REM   1. Open Command Prompt
REM   2. Navigate to: C:\Users\sayan\Desktop\New folder (4)\AUdoc_back
REM   3. Run: email_scheduler.bat
REM
REM To keep running after closing Command Prompt:
REM   - Use Windows Task Scheduler (see instructions below)
REM
REM ============================================================================

echo.
echo ============================================================================
echo  AUdoc Email Scheduler
echo ============================================================================
echo.

REM Change to project directory
cd /d "C:\Users\sayan\Desktop\New folder (4)\AUdoc_back"

if errorlevel 1 (
    echo ERROR: Could not change to project directory
    echo Expected: C:\Users\sayan\Desktop\New folder (4)\AUdoc_back
    pause
    exit /b 1
)

echo Project directory: %CD%
echo.

REM Check if virtual environment exists
if not exist "myenv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Expected: myenv\Scripts\activate.bat
    echo.
    echo Please create virtual environment first:
    echo   python -m venv myenv
    echo   myenv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Virtual environment found
echo.

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.

REM Check if schedule package is installed
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo WARNING: schedule package not found. Installing...
    pip install schedule
    echo.
)

echo ✓ All dependencies ready
echo.

REM Start the scheduler
echo ============================================================================
echo Starting Email Scheduler...
echo ============================================================================
echo.
echo Tasks:
echo   • 08:00 AM - Send appointment confirmations
echo   • 08:00 PM - Send appointment reminders
echo.
echo Log file: email_scheduler.log
echo.
echo Press Ctrl+C to stop the scheduler
echo ============================================================================
echo.

python email_scheduler.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR: Email scheduler failed!
    echo ============================================================================
    echo Check email_scheduler.log for details
    pause
    exit /b 1
)

pause
