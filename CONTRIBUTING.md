# Contributing to My Little Accountant

Thank you for your interest in contributing to My Little Accountant! This project aims to make personal finance management accessible to everyone, regardless of technical background.

## 🎯 How to Contribute

### Reporting Bugs
- Use the [GitHub Issues](https://github.com/yourusername/my-little-accountant/issues) page
- Include steps to reproduce the issue
- Attach sample files (if applicable) that cause the problem
- Specify your operating system and app version

### Suggesting Features
- Check existing issues first to avoid duplicates
- Provide a clear description of the feature
- Explain how it would benefit users
- Consider the "zero-coding" principle - features should be intuitive

### Code Contributions

#### Development Setup
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

#### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Add comments for complex logic

#### Testing
- Test with sample data before submitting
- Verify PDF processing with different bank formats
- Test on different operating systems if possible
- Ensure the executable builds successfully

#### Pull Request Process
1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Test thoroughly with sample data
4. Update documentation if needed
5. Submit a pull request with a clear description

## 🏗️ Architecture Overview

### Core Modules
- **main.py** - Streamlit web interface and main application logic
- **pdf_processor.py** - PDF bank statement extraction and parsing
- **data_cleaner.py** - Data standardization and validation
- **category_engine.py** - Smart categorization with keyword matching
- **export_utils.py** - Data export functionality (CSV, Excel, PDF)

### Key Principles
1. **Zero-coding user experience** - Everything should work out of the box
2. **Graceful error handling** - Always provide helpful error messages
3. **Progressive disclosure** - Show simple options first, advanced options later
4. **Data privacy** - All processing happens locally, no external servers

## 🧪 Testing Guidelines

### Manual Testing Checklist
- [ ] Upload CSV files with various formats
- [ ] Upload Excel files (.xlsx, .xls)
- [ ] Upload PDF bank statements from different banks
- [ ] Test categorization accuracy
- [ ] Verify export functionality
- [ ] Test auto-save and backup features
- [ ] Check responsive design on different screen sizes

### Sample Data
Use the provided sample files in `sample_files/` directory for consistent testing.

## 📝 Documentation

### Code Documentation
- Add docstrings to all public functions
- Include type hints where helpful
- Document complex algorithms or business logic

### User Documentation
- Update README.md for new features
- Add help text for new UI elements
- Update troubleshooting section for new issues

## 🚀 Release Process

### Version Numbering
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes or major new features
- MINOR: New features or significant improvements
- PATCH: Bug fixes and minor improvements

### Building Executables
```bash
# Build for current platform
python build_exe.py

# Test the executable
cd build
./setup.sh  # or setup.bat on Windows
```

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help newcomers learn
- Focus on constructive feedback
- Respect different skill levels and backgrounds

### Communication
- Use clear, jargon-free language
- Provide context for technical discussions
- Be patient with non-technical users
- Celebrate contributions of all sizes

## 🐛 Common Issues

### Development Issues
- **Import errors**: Make sure virtual environment is activated
- **Streamlit not updating**: Use `--server.runOnSave true` flag
- **PDF processing fails**: Check pdfplumber installation
- **Executable too large**: Use `--exclude-module` flags in PyInstaller

### User Issues
- **Windows Defender warnings**: Normal for new executables
- **PDF parsing errors**: Bank-specific formatting issues
- **Categorization accuracy**: Keyword matching limitations
- **Performance issues**: Large datasets or complex PDFs

## 📋 Roadmap

### Short Term (Next Release)
- [ ] Improved PDF parsing for more bank formats
- [ ] Better error messages and user guidance
- [ ] Enhanced mobile responsiveness
- [ ] More export format options

### Long Term (Future Releases)
- [ ] Budget planning features
- [ ] Goal tracking and savings targets
- [ ] Investment tracking
- [ ] Multi-currency support
- [ ] Cloud sync (optional)

## 💡 Ideas for Contributors

### Good First Issues
- Adding new bank PDF formats
- Improving error messages
- Adding more sample data files
- Enhancing mobile UI
- Writing documentation

### Advanced Features
- Machine learning for better categorization
- Advanced chart types
- Custom category creation
- Data import from other finance apps
- API integration for automatic downloads

## 📞 Getting Help

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bugs and feature requests
- **Email**: For sensitive issues or private discussions

Thank you for contributing to making personal finance management accessible to everyone! 💰

