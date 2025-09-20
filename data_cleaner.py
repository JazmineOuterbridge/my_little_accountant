"""
Data Cleaning and Standardization Module
Handles date parsing, amount standardization, and data validation
"""

import pandas as pd
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataCleaner:
    """Cleans and standardizes financial transaction data"""
    
    def __init__(self):
        # Date format patterns
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY or M/D/YYYY
            r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # MM.DD.YYYY
            r'\d{1,2}/\d{1,2}/\d{2}',   # MM/DD/YY
        ]
        
        # Amount cleaning patterns
        self.amount_patterns = [
            r'[\d,]+\.\d{2}',  # 1,234.56
            r'[\d,]+\.\d{1}',  # 1,234.5
            r'[\d,]+',         # 1,234
        ]
    
    def clean_date(self, date_str: str) -> Optional[str]:
        """Clean and standardize date format"""
        if pd.isna(date_str) or not isinstance(date_str, str):
            return None
        
        date_str = str(date_str).strip()
        
        # Try to parse different date formats
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                date_part = match.group()
                
                # Parse the date
                try:
                    # Handle MM/DD/YYYY format
                    if '/' in date_part:
                        parts = date_part.split('/')
                        if len(parts) == 3:
                            month, day, year = parts
                            if len(year) == 2:  # Convert YY to YYYY
                                year = '20' + year if int(year) < 50 else '19' + year
                            
                            # Ensure month and day are 2 digits
                            month = month.zfill(2)
                            day = day.zfill(2)
                            
                            # Validate date
                            parsed_date = datetime(int(year), int(month), int(day))
                            return parsed_date.strftime('%Y-%m-%d')
                    
                    # Handle MM-DD-YYYY format
                    elif '-' in date_part:
                        parts = date_part.split('-')
                        if len(parts) == 3:
                            if len(parts[0]) == 4:  # YYYY-MM-DD
                                year, month, day = parts
                            else:  # MM-DD-YYYY
                                month, day, year = parts
                            
                            month = month.zfill(2)
                            day = day.zfill(2)
                            
                            parsed_date = datetime(int(year), int(month), int(day))
                            return parsed_date.strftime('%Y-%m-%d')
                    
                    # Handle MM.DD.YYYY format
                    elif '.' in date_part:
                        parts = date_part.split('.')
                        if len(parts) == 3:
                            month, day, year = parts
                            month = month.zfill(2)
                            day = day.zfill(2)
                            
                            parsed_date = datetime(int(year), int(month), int(day))
                            return parsed_date.strftime('%Y-%m-%d')
                
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def clean_amount(self, amount_str) -> Optional[float]:
        """Clean and standardize amount format"""
        if pd.isna(amount_str):
            return None
        
        # Convert to string and clean
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols and extra spaces
        amount_str = re.sub(r'[$£€¥]', '', amount_str)
        amount_str = re.sub(r'\s+', '', amount_str)
        
        # Handle negative amounts
        is_negative = False
        if amount_str.startswith('-') or amount_str.startswith('(') and amount_str.endswith(')'):
            is_negative = True
            amount_str = amount_str.replace('-', '').replace('(', '').replace(')', '')
        
        # Extract numeric part
        for pattern in self.amount_patterns:
            match = re.search(pattern, amount_str)
            if match:
                numeric_str = match.group().replace(',', '')
                try:
                    amount = float(numeric_str)
                    return -amount if is_negative else amount
                except ValueError:
                    continue
        
        return None
    
    def clean_description(self, desc_str: str) -> str:
        """Clean and standardize description"""
        if pd.isna(desc_str):
            return ""
        
        desc_str = str(desc_str).strip()
        
        # Remove extra whitespace
        desc_str = re.sub(r'\s+', ' ', desc_str)
        
        # Remove common prefixes/suffixes
        desc_str = re.sub(r'^(DEBIT|CREDIT|DR|CR)\s*', '', desc_str, flags=re.IGNORECASE)
        desc_str = re.sub(r'\s*(DEBIT|CREDIT|DR|CR)$', '', desc_str, flags=re.IGNORECASE)
        
        return desc_str.strip()
    
    def clean_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
        """Clean entire DataFrame and return issues found"""
        issues = {
            'invalid_dates': [],
            'invalid_amounts': [],
            'empty_descriptions': [],
            'duplicates': []
        }
        
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Clean dates
        if 'Date' in cleaned_df.columns:
            cleaned_df['Date'] = cleaned_df['Date'].apply(self.clean_date)
            invalid_dates = cleaned_df[cleaned_df['Date'].isna()].index.tolist()
            issues['invalid_dates'] = invalid_dates
        
        # Clean amounts
        if 'Amount' in cleaned_df.columns:
            cleaned_df['Amount'] = cleaned_df['Amount'].apply(self.clean_amount)
            invalid_amounts = cleaned_df[cleaned_df['Amount'].isna()].index.tolist()
            issues['invalid_amounts'] = invalid_amounts
        
        # Clean descriptions
        if 'Description' in cleaned_df.columns:
            cleaned_df['Description'] = cleaned_df['Description'].apply(self.clean_description)
            empty_descriptions = cleaned_df[cleaned_df['Description'] == ''].index.tolist()
            issues['empty_descriptions'] = empty_descriptions
        
        # Detect potential duplicates
        if all(col in cleaned_df.columns for col in ['Date', 'Amount', 'Description']):
            # Create a hash for each transaction
            cleaned_df['_hash'] = (
                cleaned_df['Date'].astype(str) + 
                cleaned_df['Amount'].astype(str) + 
                cleaned_df['Description'].astype(str)
            ).str.lower()
            
            # Find duplicates
            duplicates = cleaned_df[cleaned_df.duplicated(subset=['_hash'], keep=False)].index.tolist()
            issues['duplicates'] = duplicates
            
            # Remove the hash column
            cleaned_df = cleaned_df.drop('_hash', axis=1)
        
        # Remove rows with critical missing data
        before_count = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=['Date', 'Amount'])
        after_count = len(cleaned_df)
        
        if before_count != after_count:
            issues['removed_rows'] = before_count - after_count
        
        return cleaned_df, issues
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """Validate cleaned data and return summary"""
        validation = {
            'total_transactions': len(df),
            'date_range': None,
            'amount_range': None,
            'total_income': 0,
            'total_expenses': 0,
            'net_flow': 0,
            'categories_needed': len(df[df.get('Category', '').isna() | (df.get('Category', '') == '')])
        }
        
        if len(df) == 0:
            return validation
        
        # Date range
        if 'Date' in df.columns and not df['Date'].isna().all():
            valid_dates = pd.to_datetime(df['Date'], errors='coerce')
            valid_dates = valid_dates.dropna()
            if len(valid_dates) > 0:
                validation['date_range'] = {
                    'start': valid_dates.min().strftime('%Y-%m-%d'),
                    'end': valid_dates.max().strftime('%Y-%m-%d')
                }
        
        # Amount range
        if 'Amount' in df.columns and not df['Amount'].isna().all():
            amounts = df['Amount'].dropna()
            if len(amounts) > 0:
                validation['amount_range'] = {
                    'min': amounts.min(),
                    'max': amounts.max(),
                    'mean': amounts.mean()
                }
                
                # Income vs expenses
                income = amounts[amounts > 0].sum()
                expenses = abs(amounts[amounts < 0].sum())
                validation['total_income'] = income
                validation['total_expenses'] = expenses
                validation['net_flow'] = income - expenses
        
        return validation

def clean_transaction_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    """Convenience function to clean transaction data"""
    cleaner = DataCleaner()
    return cleaner.clean_dataframe(df)

def validate_transaction_data(df: pd.DataFrame) -> Dict[str, any]:
    """Convenience function to validate transaction data"""
    cleaner = DataCleaner()
    return cleaner.validate_data(df)

