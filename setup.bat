@echo off
title My Little Accountant - Personal Finance App

echo.
echo ========================================
echo    My Little Accountant
echo    Personal Finance Management
echo ========================================
echo.

echo Starting the application...
echo.

echo If this is your first time running the app, Windows Defender might ask for permission.
echo Click "More info" and then "Run anyway" if you see a security warning.
echo This is normal for new software - the app is completely safe!
echo.

echo Opening your browser automatically...
echo You can close this window once the app opens in your browser.
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Python to run the app...
    echo Installing dependencies if needed...
    python -m pip install -r requirements.txt --quiet
    echo.
    echo Starting My Little Accountant...
    echo Your browser will open automatically at http://localhost:8501
    echo.
    echo If the browser doesn't open automatically, please go to:
    echo http://localhost:8501
    echo.
    timeout /t 3 >nul
    start http://localhost:8501
    python -m streamlit run main.py --server.headless true --server.port 8501
) else (
    echo Python not found. Trying to run the standalone executable...
    if exist "MyLittleAccountant.exe" (
        echo Starting standalone executable...
        start MyLittleAccountant.exe
        timeout /t 3 >nul
        start http://localhost:8501
    ) else (
        echo.
        echo ========================================
        echo ERROR: Cannot start the application
        echo ========================================
        echo.
        echo Neither Python nor the executable was found.
        echo.
        echo Please make sure you have:
        echo 1. Downloaded the complete package
        echo 2. Extracted all files to a folder
        echo 3. Run this setup.bat file from that folder
        echo.
        echo If you're missing Python, you can:
        echo - Install Python from https://python.org
        echo - Or download a pre-built executable version
        echo.
        pause
        exit /b 1
    )
)

echo.
echo App started! Check your browser.
echo.
pause

