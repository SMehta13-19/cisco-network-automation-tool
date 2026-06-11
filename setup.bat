@echo off
echo ========================================
echo Cisco Network Automation Tool - Setup
echo ========================================
echo.

echo Step 1: Creating virtual environment...
python -m venv venv

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo Step 4: Installing dependencies...
pip install -r requirements.txt

echo Step 5: Creating backups directory...
if not exist backups mkdir backups

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the automation tool:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run: python network_automation.py
echo.
pause