#!/bin/bash

# My Little Accountant - Personal Finance App Launcher
# For macOS and Linux

echo ""
echo "========================================"
echo "   My Little Accountant"
echo "   Personal Finance Management"
echo "========================================"
echo ""

echo "Starting the application..."
echo ""

echo "If this is your first time running the app, you might need to:"
echo "1. Right-click and select 'Open' instead of double-clicking"
echo "2. Click 'Open' when macOS asks about the unidentified developer"
echo "3. This is normal for new software - the app is completely safe!"
echo ""

echo "Opening your browser automatically..."
echo "You can close this terminal once the app opens in your browser."
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "Using Python to run the app..."
    python3 -m streamlit run main.py --server.headless true --server.port 8501
elif command -v python &> /dev/null; then
    echo "Using Python to run the app..."
    python -m streamlit run main.py --server.headless true --server.port 8501
else
    echo "Python not found. Trying to run the standalone executable..."
    if [ -f "MyLittleAccountant" ]; then
        chmod +x MyLittleAccountant
        ./MyLittleAccountant
    elif [ -d "MyLittleAccountant.app" ]; then
        open MyLittleAccountant.app
    else
        echo "Error: Neither Python nor the executable was found."
        echo "Please make sure you have downloaded the complete package."
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo ""
echo "App started! Check your browser."
echo ""
read -p "Press Enter to exit..."

