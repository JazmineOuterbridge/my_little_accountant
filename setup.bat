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
    python -m streamlit run main.py --server.headless true --server.port 8501
) else (
    echo Python not found. Trying to run the standalone executable...
    if exist "MyLittleAccountant.exe" (
        start MyLittleAccountant.exe
    ) else (
        echo Error: Neither Python nor the executable was found.
        echo Please make sure you have downloaded the complete package.
        pause
        exit /b 1
    )
)

echo.
echo App started! Check your browser.
echo.
pause

