@echo off
title Building My Little Accountant Executable

echo.
echo ========================================
echo    My Little Accountant - Builder
echo    Creating Standalone Executable
echo ========================================
echo.

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo Building executable...
python build_exe.py

echo.
echo Build complete! Check the 'build' folder for your executable.
echo.
pause

