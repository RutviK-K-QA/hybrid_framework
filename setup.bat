@echo off
REM Quick Setup Script for RAAPID Python Automation Framework

echo ============================================
echo RAAPID Automation Framework Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Python detected
python --version
echo.

REM Create virtual environment
echo [2/4] Creating virtual environment...
python -m venv venv
echo Virtual environment created successfully
echo.

REM Activate virtual environment and install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed successfully
echo.

REM Install Playwright browsers
echo [4/4] Installing Playwright browsers...
playwright install chromium
echo Playwright browsers installed successfully
echo.

echo ============================================
echo Setup completed successfully!
echo ============================================
echo.
echo To activate the virtual environment, run:
echo     venv\Scripts\activate
echo.
echo To run tests, use:
echo     pytest tests/
echo.
echo For more information, see README.md
echo.
pause

