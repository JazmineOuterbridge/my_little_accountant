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
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp

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
        """Process PDF and extract transactions with enhanced speed and progress tracking"""
        start_time = time.time()
        
        try:
            if progress_callback:
                progress_callback("Reading PDF file...", 0, "Starting PDF processing")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                raise ValueError("Could not extract text from PDF")
            
            if progress_callback:
                progress_callback("Detecting bank format...", 20, "Text extracted successfully")
            
            # Detect bank type
            bank_type = self.detect_bank(text)
            
            if progress_callback:
                progress_callback(f"Processing {bank_type} format...", 40, f"Bank type: {bank_type}")
            
            # Split into lines and clean with parallel processing
            lines = text.split('\n')
            cleaned_lines = []
            
            # Use list comprehension for faster line cleaning
            cleaned_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
            
            if progress_callback:
                progress_callback("Parsing transactions...", 60, f"Processing {len(cleaned_lines)} lines")
            
            # Extract transactions with progress tracking
            transactions = []
            total_lines = len(cleaned_lines)
            
            for i, line in enumerate(cleaned_lines):
                transaction = self.parse_transaction_line(line, bank_type)
                if transaction:
                    transactions.append(transaction)
                
                # Update progress every 10% of lines
                if progress_callback and i % max(1, total_lines // 10) == 0:
                    progress = 60 + (i / total_lines) * 20  # 60-80% for parsing
                    progress_callback(f"Parsed {i}/{total_lines} lines...", progress, f"Found {len(transactions)} transactions so far")
            
            # If no transactions found with line-by-line parsing, try table extraction
            if not transactions:
                if progress_callback:
                    progress_callback("Trying table extraction...", 80, "Line parsing failed, trying tables")
                transactions = self.extract_from_tables(pdf_path)
            
            processing_time = time.time() - start_time
            
            if progress_callback:
                progress_callback(f"Found {len(transactions)} transactions", 100, f"Completed in {processing_time:.2f}s")
            
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
        """Process multiple PDF files with parallel processing and enhanced progress tracking"""
        start_time = time.time()
        all_transactions = []
        
        # Use parallel processing for multiple PDFs
        max_workers = min(len(pdf_paths), mp.cpu_count())
        
        def process_single_pdf(pdf_path):
            """Process a single PDF file"""
            try:
                # Create a callback that includes file-specific progress
                def file_progress_callback(message, progress, details):
                    if progress_callback:
                        filename = pdf_path.split('/')[-1] if '/' in pdf_path else pdf_path.split('\\')[-1]
                        progress_callback(f"[{filename}] {message}", progress, details)
                
                df = self.process_pdf(pdf_path, file_progress_callback)
                return df if not df.empty else None
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                return None
        
        # Process PDFs in parallel for better performance
        if len(pdf_paths) > 1:
            if progress_callback:
                progress_callback("Starting parallel PDF processing...", 0, f"Processing {len(pdf_paths)} PDFs with {max_workers} workers")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all PDF processing tasks
                future_to_pdf = {executor.submit(process_single_pdf, pdf_path): pdf_path for pdf_path in pdf_paths}
                
                completed = 0
                for future in as_completed(future_to_pdf):
                    pdf_path = future_to_pdf[future]
                    completed += 1
                    
                    try:
                        df = future.result()
                        if df is not None:
                            all_transactions.append(df)
                        
                        if progress_callback:
                            progress = (completed / len(pdf_paths)) * 100
                            progress_callback(f"Completed {completed}/{len(pdf_paths)} PDFs", progress, f"Processed: {pdf_path}")
                    
                    except Exception as e:
                        logger.error(f"Error processing {pdf_path}: {e}")
                        if progress_callback:
                            progress = (completed / len(pdf_paths)) * 100
                            progress_callback(f"Error in {pdf_path}", progress, f"Error: {str(e)}")
        else:
            # Single PDF processing
            for i, pdf_path in enumerate(pdf_paths):
                if progress_callback:
                    progress_callback(f"Processing PDF {i+1} of {len(pdf_paths)}: {pdf_path}", 0, "Starting single PDF processing")
                
                try:
                    df = self.process_pdf(pdf_path, progress_callback)
                    if not df.empty:
                        all_transactions.append(df)
                except Exception as e:
                    logger.error(f"Error processing {pdf_path}: {e}")
                    continue
        
        processing_time = time.time() - start_time
        
        if all_transactions:
            if progress_callback:
                total_transactions = sum(len(df) for df in all_transactions)
                progress_callback(f"Combining {len(all_transactions)} PDFs...", 90, f"Total transactions: {total_transactions}")
            
            combined_df = pd.concat(all_transactions, ignore_index=True)
            
            if progress_callback:
                progress_callback(f"✅ Processing complete!", 100, f"Combined {len(all_transactions)} PDFs into {len(combined_df)} transactions in {processing_time:.2f}s")
            
            return combined_df
        else:
            if progress_callback:
                progress_callback("❌ No transactions found", 100, f"Processed {len(pdf_paths)} PDFs in {processing_time:.2f}s")
            return pd.DataFrame(columns=['Date', 'Description', 'Amount'])

def process_pdf_file(pdf_path: str, progress_callback=None) -> pd.DataFrame:
    """Convenience function to process a single PDF"""
    processor = BankPDFProcessor()
    return processor.process_pdf(pdf_path, progress_callback)

def process_pdf_files(pdf_paths: List[str], progress_callback=None) -> pd.DataFrame:
    """Convenience function to process multiple PDFs"""
    processor = BankPDFProcessor()
    return processor.process_multiple_pdfs(pdf_paths, progress_callback)

