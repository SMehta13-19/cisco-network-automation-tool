@echo off
echo Starting Cisco Network Automation Tool...
echo.

REM Activate virtual environment and run the script
call venv\Scripts\activate.bat
python network_automation.py

echo.
echo Automation completed. Check network_automation.log for details.
pause