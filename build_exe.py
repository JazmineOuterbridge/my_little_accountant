"""
PyInstaller Build Script for My Little Accountant
Creates standalone executables for Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def get_platform_specs():
    """Get platform-specific build specifications"""
    system = platform.system().lower()
    
    specs = {
        'windows': {
            'extension': '.exe',
            'onefile_args': ['--onefile', '--windowed', '--console'],
            'onedir_args': ['--onedir', '--windowed', '--console'],
            'icon': 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
            'name': 'MyLittleAccountant'
        },
        'darwin': {  # macOS
            'extension': '.app',
            'onefile_args': ['--onefile', '--windowed'],
            'onedir_args': ['--onedir', '--windowed'],
            'icon': 'assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
            'name': 'MyLittleAccountant'
        },
        'linux': {
            'extension': '',
            'onefile_args': ['--onefile', '--windowed'],
            'onedir_args': ['--onedir', '--windowed'],
            'icon': 'assets/icon.png' if os.path.exists('assets/icon.png') else None,
            'name': 'MyLittleAccountant'
        }
    }
    
    return specs.get(system, specs['linux'])

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('sample_files', 'sample_files'),
        ('assets', 'assets'),
        ('*.py', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'pdfplumber',
        'openpyxl',
        'reportlab',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner',
        'streamlit.runtime.state',
        'streamlit.elements.lib.column_config_utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyLittleAccountant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('MyLittleAccountant.spec', 'w') as f:
        f.write(spec_content)

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    # Install PyInstaller if not already installed
    try:
        import PyInstaller
        print("PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Install other dependencies
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)

def build_executable():
    """Build the executable"""
    system = platform.system().lower()
    specs = get_platform_specs()
    
    print(f"Building for {system}...")
    
    # Create directories
    os.makedirs('build', exist_ok=True)
    os.makedirs('dist', exist_ok=True)
    
    # Create spec file
    create_spec_file()
    
    # Build command
    build_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'MyLittleAccountant.spec'
    ]
    
    # Add platform-specific arguments
    if specs['icon'] and os.path.exists(specs['icon']):
        build_cmd.extend(['--icon', specs['icon']])
    
    print(f"Running: {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        
        # Move executable to build directory
        if system == 'windows':
            exe_name = f"{specs['name']}.exe"
        elif system == 'darwin':
            exe_name = f"{specs['name']}.app"
        else:
            exe_name = specs['name']
        
        if os.path.exists(f"dist/{exe_name}"):
            shutil.move(f"dist/{exe_name}", f"build/{exe_name}")
            print(f"Executable created: build/{exe_name}")
        
        # Clean up
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('build'):
            # Keep only the executable
            for item in os.listdir('build'):
                if item != exe_name:
                    item_path = os.path.join('build', item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_launcher_scripts():
    """Create launcher scripts for different platforms"""
    
    # Windows batch file
    windows_script = '''@echo off
echo Starting My Little Accountant...
echo.
echo If this is your first time running the app, Windows Defender might ask for permission.
echo Click "More info" and then "Run anyway" if you see a security warning.
echo.
pause
MyLittleAccountant.exe
pause
'''
    
    with open('build/setup.bat', 'w') as f:
        f.write(windows_script)
    
    # macOS/Linux shell script
    unix_script = '''#!/bin/bash
echo "Starting My Little Accountant..."
echo ""
echo "If this is your first time running the app, you might need to:"
echo "1. Right-click and select 'Open' instead of double-clicking"
echo "2. Click 'Open' when macOS asks about the unidentified developer"
echo ""

# Make executable
chmod +x MyLittleAccountant

# Run the app
./MyLittleAccountant
'''
    
    with open('build/setup.sh', 'w') as f:
        f.write(unix_script)
    
    # Make shell script executable
    if platform.system().lower() != 'windows':
        os.chmod('build/setup.sh', 0o755)

def create_readme():
    """Create README for the build"""
    readme_content = '''# My Little Accountant - Standalone Executable

## 🚀 Quick Start (Zero Coding Required!)

### For Windows Users:
1. **Download** the ZIP file and extract it anywhere on your computer
2. **Double-click** `setup.bat` 
3. **Your browser will open automatically** with the app!

### For Mac Users:
1. **Download** the ZIP file and extract it anywhere on your computer
2. **Right-click** `setup.sh` and select "Open" (or double-click if it works)
3. **Your browser will open automatically** with the app!

### For Linux Users:
1. **Download** the ZIP file and extract it anywhere on your computer
2. **Open Terminal** in the extracted folder
3. **Run** `chmod +x setup.sh && ./setup.sh`
4. **Your browser will open automatically** with the app!

## 📁 What's Included:
- `MyLittleAccountant.exe` (Windows) / `MyLittleAccountant.app` (Mac) / `MyLittleAccountant` (Linux)
- `setup.bat` / `setup.sh` - Easy launcher scripts
- Sample data files to try the app
- This README file

## ❓ Troubleshooting:

### "Windows protected your PC" / "Unidentified Developer"
- Click "More info" then "Run anyway"
- This is normal for new software - the app is completely safe!

### App won't start / Browser doesn't open
- Make sure you have internet connection (for the first run)
- Try running `setup.bat` / `setup.sh` as administrator
- Check if your antivirus is blocking the app

### PDF files not working
- Make sure the PDF is a bank statement (not a receipt or invoice)
- Try converting to CSV format first
- Check if the PDF is password protected

### Data not saving
- The app saves automatically every 30 seconds
- Make sure you have write permissions in the app folder
- Try creating a manual backup using the Export button

## 🆘 Need Help?
- Check the Help section in the app (❓ icon in sidebar)
- Try the sample data first to see how it works
- Look for tooltips (❓) throughout the app

## 🔒 Privacy & Security:
- All your data stays on your computer
- No data is sent to external servers
- The app only connects to the internet for initial setup
- You can run it completely offline after first use

---
**My Little Accountant** - Making personal finance simple for everyone! 💰
'''
    
    with open('build/README.md', 'w') as f:
        f.write(readme_content)

def main():
    """Main build function"""
    print("=== My Little Accountant - Executable Builder ===")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: main.py not found. Please run this script from the project root directory.")
        return False
    
    try:
        # Install dependencies
        install_dependencies()
        
        # Create necessary directories
        os.makedirs('assets', exist_ok=True)
        os.makedirs('sample_files', exist_ok=True)
        
        # Build executable
        if build_executable():
            print("\n✅ Build completed successfully!")
            
            # Create launcher scripts
            create_launcher_scripts()
            
            # Create README
            create_readme()
            
            # Copy sample files
            if os.path.exists('sample_files'):
                shutil.copytree('sample_files', 'build/sample_files', dirs_exist_ok=True)
            
            print("\n📦 Executable package created in 'build/' directory")
            print("\n🎉 Ready to distribute! Users can:")
            print("   1. Download the build folder as ZIP")
            print("   2. Extract anywhere")
            print("   3. Double-click setup.bat/setup.sh")
            print("   4. Browser opens automatically!")
            
            return True
        else:
            print("\n❌ Build failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

