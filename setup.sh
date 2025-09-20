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
    echo "Installing dependencies if needed..."
    python3 -m pip install -r requirements.txt --quiet
    echo ""
    echo "Starting My Little Accountant..."
    echo "Your browser will open automatically at http://localhost:8501"
    echo ""
    echo "If the browser doesn't open automatically, please go to:"
    echo "http://localhost:8501"
    echo ""
    sleep 3
    open http://localhost:8501 2>/dev/null || xdg-open http://localhost:8501 2>/dev/null || echo "Please open http://localhost:8501 in your browser"
    python3 -m streamlit run main.py --server.headless true --server.port 8501
elif command -v python &> /dev/null; then
    echo "Using Python to run the app..."
    echo "Installing dependencies if needed..."
    python -m pip install -r requirements.txt --quiet
    echo ""
    echo "Starting My Little Accountant..."
    echo "Your browser will open automatically at http://localhost:8501"
    echo ""
    echo "If the browser doesn't open automatically, please go to:"
    echo "http://localhost:8501"
    echo ""
    sleep 3
    open http://localhost:8501 2>/dev/null || xdg-open http://localhost:8501 2>/dev/null || echo "Please open http://localhost:8501 in your browser"
    python -m streamlit run main.py --server.headless true --server.port 8501
else
    echo "Python not found. Trying to run the standalone executable..."
    if [ -f "MyLittleAccountant" ]; then
        chmod +x MyLittleAccountant
        echo "Starting standalone executable..."
        ./MyLittleAccountant &
        sleep 3
        open http://localhost:8501 2>/dev/null || xdg-open http://localhost:8501 2>/dev/null || echo "Please open http://localhost:8501 in your browser"
    elif [ -d "MyLittleAccountant.app" ]; then
        echo "Starting macOS application..."
        open MyLittleAccountant.app
        sleep 3
        open http://localhost:8501 2>/dev/null || echo "Please open http://localhost:8501 in your browser"
    else
        echo ""
        echo "========================================"
        echo "ERROR: Cannot start the application"
        echo "========================================"
        echo ""
        echo "Neither Python nor the executable was found."
        echo ""
        echo "Please make sure you have:"
        echo "1. Downloaded the complete package"
        echo "2. Extracted all files to a folder"
        echo "3. Run this setup.sh file from that folder"
        echo ""
        echo "If you're missing Python, you can:"
        echo "- Install Python from https://python.org"
        echo "- Or download a pre-built executable version"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo ""
echo "App started! Check your browser."
echo ""
read -p "Press Enter to exit..."

