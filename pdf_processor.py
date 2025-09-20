"""
PDF Bank Statement Processor
Handles extraction of transaction data from various bank PDF formats
"""

import pdfplumber
import pandas as pd
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankPDFProcessor:
    """Processes bank statement PDFs and extracts transaction data"""
    
    def __init__(self):
        # Bank-specific patterns for major US and Bermuda banks
        self.bank_patterns = {
            'chase': {
                'date_pattern': r'\d{2}/\d{2}/\d{4}',
                'amount_pattern': r'[\d,]+\.\d{2}',
                'transaction_start': r'^\d{2}/\d{2}',
                'skip_lines': ['DATE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
            },
            'bank_of_america': {
                'date_pattern': r'\d{2}/\d{2}/\d{4}',
                'amount_pattern': r'[\d,]+\.\d{2}',
                'transaction_start': r'^\d{2}/\d{2}',
                'skip_lines': ['DATE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
            },
            'wells_fargo': {
                'date_pattern': r'\d{2}/\d{2}/\d{4}',
                'amount_pattern': r'[\d,]+\.\d{2}',
                'transaction_start': r'^\d{2}/\d{2}',
                'skip_lines': ['DATE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
            },
            'citibank': {
                'date_pattern': r'\d{2}/\d{2}/\d{4}',
                'amount_pattern': r'[\d,]+\.\d{2}',
                'transaction_start': r'^\d{2}/\d{2}',
                'skip_lines': ['DATE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
            },
            'hsbc_bermuda': {
                'date_pattern': r'\d{2}/\d{2}/\d{4}',
                'amount_pattern': r'[\d,]+\.\d{2}',
                'transaction_start': r'^\d{2}/\d{2}',
                'skip_lines': ['DATE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
            },
            'butterfield_bermuda': {
                'date_pattern': r'\d{2}/\d{2}/\d{4}',
                'amount_pattern': r'[\d,]+\.\d{2}',
                'transaction_start': r'^\d{2}/\d{2}',
                'skip_lines': ['DATE', 'DESCRIPTION', 'AMOUNT', 'BALANCE']
            }
        }
    
    def detect_bank(self, text: str) -> str:
        """Detect bank type from PDF text"""
        text_lower = text.lower()
        
        if 'chase' in text_lower or 'jpmorgan' in text_lower:
            return 'chase'
        elif 'bank of america' in text_lower or 'bofa' in text_lower:
            return 'bank_of_america'
        elif 'wells fargo' in text_lower:
            return 'wells_fargo'
        elif 'citibank' in text_lower or 'citi' in text_lower:
            return 'citibank'
        elif 'hsbc' in text_lower:
            return 'hsbc_bermuda'
        elif 'butterfield' in text_lower:
            return 'butterfield_bermuda'
        else:
            return 'generic'
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def parse_transaction_line(self, line: str, bank_type: str) -> Optional[Dict]:
        """Parse a single transaction line"""
        if not line.strip():
            return None
            
        # Skip header lines
        skip_words = self.bank_patterns.get(bank_type, {}).get('skip_lines', [])
        if any(skip_word.lower() in line.lower() for skip_word in skip_words):
            return None
        
        # Enhanced date patterns for various formats
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
            r'\d{1,2}/\d{1,2}/\d{2}',  # M/D/YY
        ]
        
        date_match = None
        date_str = None
        
        for pattern in date_patterns:
            date_match = re.search(pattern, line)
            if date_match:
                date_str = date_match.group()
                break
        
        if not date_match:
            return None
        
        # Enhanced amount patterns
        amount_patterns = [
            r'(-?\$?\s?[\d,]+\.\d{2})',  # Standard amount with optional negative and dollar sign
            r'(-?\$?\s?[\d,]+\d{2})',    # Amount without decimal point
            r'(-?\$?\s?[\d,]+)',         # Amount without cents
            r'(-?[\d,]+\.\d{2})',        # Standard amount with optional negative
            r'(-?[\d,]+\.\d{1})',        # Amount with one decimal place
        ]
        
        amount = None
        amount_match = None
        
        for pattern in amount_patterns:
            amount_match = re.search(pattern, line)
            if amount_match:
                amount_str = amount_match.group().replace('$', '').replace(',', '').strip()
                try:
                    amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        if amount is None:
            return None
        
        # Extract description (everything between date and amount)
        date_end = date_match.end()
        amount_start = line.find(amount_match.group())
        
        description = line[date_end:amount_start].strip()
        
        # Clean up description - remove reference numbers and extra whitespace
        description = re.sub(r'\s+', ' ', description)  # Remove extra whitespace
        description = re.sub(r'^\d+\s*', '', description)  # Remove leading reference numbers
        description = description.strip()
        
        if not description or len(description) < 3:
            return None
        
        return {
            'date': date_str,
            'description': description,
            'amount': amount
        }
    
    def process_pdf(self, pdf_path: str, progress_callback=None) -> pd.DataFrame:
        """Process PDF and extract transactions"""
        try:
            if progress_callback:
                progress_callback("Reading PDF file...")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                raise ValueError("Could not extract text from PDF")
            
            if progress_callback:
                progress_callback("Detecting bank format...")
            
            # Detect bank type
            bank_type = self.detect_bank(text)
            
            if progress_callback:
                progress_callback(f"Processing {bank_type} format...")
            
            # Split into lines and clean
            lines = text.split('\n')
            cleaned_lines = []
            
            # Clean and filter lines
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:  # Skip very short lines
                    cleaned_lines.append(line)
            
            # Extract transactions
            transactions = []
            for line in cleaned_lines:
                transaction = self.parse_transaction_line(line, bank_type)
                if transaction:
                    transactions.append(transaction)
            
            # If no transactions found with line-by-line parsing, try table extraction
            if not transactions:
                if progress_callback:
                    progress_callback("Trying table extraction...")
                transactions = self.extract_from_tables(pdf_path)
            
            if progress_callback:
                progress_callback(f"Found {len(transactions)} transactions")
            
            # Create DataFrame
            if transactions:
                df = pd.DataFrame(transactions)
                # Ensure proper column names
                df.columns = ['Date', 'Description', 'Amount']
                return df
            else:
                # Return empty DataFrame with correct structure
                return pd.DataFrame(columns=['Date', 'Description', 'Amount'])
                
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def extract_from_tables(self, pdf_path: str) -> List[Dict]:
        """Extract transactions from PDF tables using pdfplumber"""
        transactions = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract tables
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table:
                            continue
                        
                        # Look for table with date, description, amount columns
                        for row in table:
                            if not row or len(row) < 3:
                                continue
                            
                            # Try to parse row as transaction
                            row_text = ' '.join([str(cell) for cell in row if cell])
                            transaction = self.parse_transaction_line(row_text, 'generic')
                            
                            if transaction:
                                transactions.append(transaction)
                                
        except Exception as e:
            logger.error(f"Error extracting from tables: {e}")
        
        return transactions
    
    def process_multiple_pdfs(self, pdf_paths: List[str], progress_callback=None) -> pd.DataFrame:
        """Process multiple PDF files"""
        all_transactions = []
        
        for i, pdf_path in enumerate(pdf_paths):
            if progress_callback:
                progress_callback(f"Processing PDF {i+1} of {len(pdf_paths)}: {pdf_path}")
            
            try:
                df = self.process_pdf(pdf_path, progress_callback)
                if not df.empty:
                    all_transactions.append(df)
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        if all_transactions:
            combined_df = pd.concat(all_transactions, ignore_index=True)
            return combined_df
        else:
            return pd.DataFrame(columns=['Date', 'Description', 'Amount'])

def process_pdf_file(pdf_path: str, progress_callback=None) -> pd.DataFrame:
    """Convenience function to process a single PDF"""
    processor = BankPDFProcessor()
    return processor.process_pdf(pdf_path, progress_callback)

def process_pdf_files(pdf_paths: List[str], progress_callback=None) -> pd.DataFrame:
    """Convenience function to process multiple PDFs"""
    processor = BankPDFProcessor()
    return processor.process_multiple_pdfs(pdf_paths, progress_callback)

