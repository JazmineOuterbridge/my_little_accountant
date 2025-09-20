#!/bin/bash

# My Little Accountant - Executable Builder
# For macOS and Linux

echo ""
echo "========================================"
echo "   My Little Accountant - Builder"
echo "   Creating Standalone Executable"
echo "========================================"
echo ""

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

echo ""
echo "Building executable..."
python3 build_exe.py

echo ""
echo "Build complete! Check the 'build' folder for your executable."
echo ""
read -p "Press Enter to exit..."

