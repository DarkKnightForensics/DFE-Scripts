@echo off
REM This batch file installs required Python libraries for CyberTip Extractor
REM Make sure Python and pip are installed and added to PATH

pip install --upgrade pip
pip install -r requirements.txt

echo.
echo All required libraries have been installed.
pause
