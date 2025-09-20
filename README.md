# 💰 My Little Accountant

**A user-friendly personal finance management application designed for individuals with zero coding experience.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🎯 What is My Little Accountant?

My Little Accountant is a simple, powerful web-based personal finance application that helps you organize and understand your spending without any technical knowledge required. Simply upload your bank statements (CSV, Excel, or PDF), let the app automatically categorize your transactions, and gain insights into your financial habits.

## ✨ Key Features

### 🚀 Zero-Coding Setup
- **One-click executable** - Download and run immediately
- **No Python installation** required
- **No command-line** interaction needed
- **Automatic browser launch** - Just double-click and go!

### 📁 Smart File Processing
- **Drag-and-drop interface** for multiple files
- **PDF bank statement conversion** - Automatically extracts transactions from PDFs
- **Multiple format support** - CSV, Excel (.xlsx), and PDF files
- **Bank-specific parsing** - Optimized for major US and Bermuda banks
- **Automatic data cleaning** - Standardizes dates, amounts, and descriptions

### 🏷️ Intelligent Categorization
- **Auto-categorization** using smart keyword matching
- **Pre-built categories** - Income, Food & Dining, Housing, Utilities, Transportation, Entertainment, Healthcare, Shopping, Education, Travel
- **Bulk categorization** tools for quick organization
- **Easy manual editing** with dropdown menus
- **Progress tracking** - See how much you've categorized

### 📊 Visual Dashboard
- **Financial overview** - Total income, expenses, and net cash flow
- **Interactive charts** - Spending by category, monthly trends
- **Time filtering** - View by year and month
- **Category breakdown** with detailed statistics
- **Export capabilities** - Download reports as CSV, Excel, or PDF

### 💾 Data Management
- **Auto-save** every 30 seconds
- **Manual backup** creation
- **Export options** - CSV, Excel, and PDF reports
- **Sample data** included for testing

## 🚀 Quick Start Guide

### For End Users (Zero Coding Required!)

#### Windows Users:
1. **Download** the latest release ZIP file from GitHub
2. **Extract** the ZIP file anywhere on your computer
3. **Double-click** `setup.bat`
4. **Your browser opens automatically** with the app!
   - If Windows Defender shows a warning, click "More info" then "Run anyway"

#### Mac Users:
1. **Download** the latest release ZIP file from GitHub
2. **Extract** the ZIP file anywhere on your computer
3. **Right-click** `setup.sh` and select "Open"
   - If macOS shows an "unidentified developer" warning, click "Open" anyway
4. **Your browser opens automatically** with the app!

#### Linux Users:
1. **Download** the latest release ZIP file from GitHub
2. **Extract** the ZIP file anywhere on your computer
3. **Open Terminal** in the extracted folder
4. **Run** `chmod +x setup.sh && ./setup.sh`
5. **Your browser opens automatically** with the app!

### First Time Setup:
1. **Upload your bank statements** - Drag and drop CSV, Excel, or PDF files
2. **Review auto-categorization** - The app automatically categorizes most transactions
3. **Manual adjustments** - Use the categorization tab to fine-tune categories
4. **View your dashboard** - See spending patterns and financial insights

## 🛠️ For Developers

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/my-little-accountant.git
cd my-little-accountant

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run main.py
```

### Building Executables
```bash
# Build standalone executable for your platform
python build_exe.py
```

The executable will be created in the `build/` directory with all necessary files for distribution.

### Project Structure
```
my-little-accountant/
├── main.py                 # Main Streamlit application
├── pdf_processor.py        # PDF extraction logic
├── data_cleaner.py         # Data standardization
├── category_engine.py      # Smart categorization
├── export_utils.py         # File exports
├── build_exe.py           # PyInstaller configuration
├── requirements.txt       # Python dependencies
├── sample_files/          # Example data files
│   ├── sample_chase.csv
│   └── sample_wellsfargo.xlsx
├── build/                 # Generated executables
│   ├── MyLittleAccountant.exe
│   ├── setup.bat
│   └── setup.sh
└── README.md             # This file
```

## 📋 Supported File Formats

### CSV Files
Expected columns: `Date`, `Description`, `Amount`
- Date format: MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD
- Amount: Positive for income, negative for expenses

### Excel Files (.xlsx, .xls)
Same format as CSV files with proper column headers.

### PDF Bank Statements
Automatically extracts transaction data from:
- **Chase Bank**
- **Bank of America**
- **Wells Fargo**
- **Citibank**
- **HSBC Bermuda**
- **Butterfield Bank (Bermuda)**
- **Generic bank formats**

## 🏷️ Category System

The app includes pre-built categories with smart keyword matching:

| Category | Keywords |
|----------|----------|
| **Income** | salary, paycheck, deposit, transfer in, interest, dividend |
| **Food & Dining** | grocery, restaurant, coffee, lunch, dinner, starbucks, mcdonalds |
| **Housing** | rent, mortgage, property tax, hoa, maintenance |
| **Utilities** | electric, water, internet, phone, cable, gas bill |
| **Transportation** | gas, uber, lyft, parking, transit, car payment, insurance |
| **Entertainment** | netflix, movie, concert, amazon, streaming, spotify |
| **Healthcare** | doctor, hospital, pharmacy, medical, prescription, cvs |
| **Shopping** | amazon, target, walmart, retail, clothing, electronics |
| **Education** | school, tuition, education, book, university, training |
| **Travel** | hotel, flight, airline, travel, vacation, booking |
| **Other** | Default category for uncategorized transactions |

## 🔧 Troubleshooting

### Common Issues

#### "Windows protected your PC" / "Unidentified Developer"
- **Solution**: Click "More info" then "Run anyway"
- **Why**: This is normal for new software - the app is completely safe!

#### App won't start / Browser doesn't open
- **Solution**: Make sure you have internet connection for first run
- **Alternative**: Try running setup.bat/setup.sh as administrator
- **Check**: Ensure your antivirus isn't blocking the app

#### PDF files not working
- **Solution**: Ensure the PDF is a bank statement (not receipt/invoice)
- **Alternative**: Try converting to CSV format first
- **Check**: Make sure the PDF isn't password protected

#### Data not saving
- **Solution**: The app saves automatically every 30 seconds
- **Check**: Ensure you have write permissions in the app folder
- **Backup**: Use the Export button to create manual backups

#### Categories look wrong
- **Solution**: Use the bulk categorization feature in the app
- **Improvement**: Categories improve with more data over time

### Getting Help

1. **In-app help** - Click ❓ icons throughout the app
2. **Sample data** - Try the included sample files first
3. **Help section** - Check the sidebar help panel
4. **GitHub Issues** - Report bugs or request features

## 🔒 Privacy & Security

- **Local data only** - All your data stays on your computer
- **No external servers** - No data is sent to external servers
- **Offline capable** - Runs completely offline after first use
- **Open source** - Full source code available for review

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/my-little-accountant.git
cd my-little-accountant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run main.py --server.runOnSave true
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- PDF processing powered by [pdfplumber](https://github.com/jsvine/pdfplumber)
- Data visualization using [Plotly](https://plotly.com/)
- Executable packaging with [PyInstaller](https://pyinstaller.org/)

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/my-little-accountant/issues)
- **Documentation**: Check the in-app help system
- **Sample Files**: Use included sample data to test functionality

---

**My Little Accountant** - Making personal finance simple for everyone! 💰

*No coding experience required. Just download, double-click, and start organizing your finances!*

