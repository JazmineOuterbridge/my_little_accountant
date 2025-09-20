"""
Smart Categorization Engine
Handles automatic and manual categorization of transactions
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class CategoryEngine:
    """Handles automatic categorization of financial transactions"""
    
    def __init__(self):
        # Pre-defined categories with keywords
        self.categories = {
            'Income': {
                'keywords': [
                    'salary', 'paycheck', 'pay roll', 'deposit', 'transfer in',
                    'direct deposit', 'refund', 'cashback', 'reward', 'bonus',
                    'interest', 'dividend', 'pension', 'social security'
                ],
                'color': '#28a745'  # Green
            },
            'Food & Dining': {
                'keywords': [
                    'grocery', 'restaurant', 'starbucks', 'mcdonalds', 'subway',
                    'pizza', 'food', 'dining', 'coffee', 'lunch', 'dinner',
                    'breakfast', 'cafe', 'bakery', 'delivery', 'takeout',
                    'whole foods', 'trader joe', 'walmart', 'target', 'costco'
                ],
                'color': '#ffc107'  # Yellow
            },
            'Housing': {
                'keywords': [
                    'rent', 'mortgage', 'housing', 'apartment', 'home',
                    'property tax', 'homeowner', 'hoa', 'maintenance'
                ],
                'color': '#6f42c1'  # Purple
            },
            'Utilities': {
                'keywords': [
                    'electric', 'electricity', 'water', 'internet', 'phone',
                    'cable', 'gas bill', 'utility', 'sewer', 'trash',
                    'verizon', 'at&t', 'comcast', 'spectrum'
                ],
                'color': '#17a2b8'  # Teal
            },
            'Transportation': {
                'keywords': [
                    'gas', 'gasoline', 'fuel', 'uber', 'lyft', 'taxi',
                    'parking', 'transit', 'bus', 'train', 'metro',
                    'car payment', 'auto loan', 'insurance', 'dmv',
                    'maintenance', 'repair', 'toll'
                ],
                'color': '#fd7e14'  # Orange
            },
            'Entertainment': {
                'keywords': [
                    'netflix', 'movie', 'concert', 'amazon', 'streaming',
                    'spotify', 'hulu', 'disney', 'youtube', 'gaming',
                    'theater', 'show', 'ticket', 'entertainment'
                ],
                'color': '#e83e8c'  # Pink
            },
            'Healthcare': {
                'keywords': [
                    'doctor', 'hospital', 'pharmacy', 'medical', 'health',
                    'dentist', 'vision', 'prescription', 'clinic', 'cvs',
                    'walgreens', 'insurance', 'copay'
                ],
                'color': '#dc3545'  # Red
            },
            'Shopping': {
                'keywords': [
                    'amazon', 'target', 'walmart', 'costco', 'best buy',
                    'shopping', 'store', 'retail', 'clothing', 'shoes',
                    'electronics', 'home depot', 'lowes'
                ],
                'color': '#6c757d'  # Gray
            },
            'Education': {
                'keywords': [
                    'school', 'tuition', 'education', 'book', 'university',
                    'college', 'student', 'course', 'training'
                ],
                'color': '#20c997'  # Green
            },
            'Travel': {
                'keywords': [
                    'hotel', 'flight', 'airline', 'travel', 'vacation',
                    'booking', 'expedia', 'airbnb', 'rental car'
                ],
                'color': '#6610f2'  # Indigo
            },
            'Other': {
                'keywords': [],
                'color': '#6c757d'  # Gray
            }
        }
        
        # Create reverse lookup for quick access
        self.keyword_to_category = {}
        for category, data in self.categories.items():
            for keyword in data['keywords']:
                self.keyword_to_category[keyword.lower()] = category
    
    def categorize_transaction(self, description: str, amount: float = None) -> str:
        """Categorize a single transaction based on description"""
        if not description:
            return 'Other'
        
        desc_lower = description.lower()
        
        # Check for exact keyword matches
        for keyword, category in self.keyword_to_category.items():
            if keyword in desc_lower:
                return category
        
        # Check for partial matches (for compound words)
        words = desc_lower.split()
        for word in words:
            if word in self.keyword_to_category:
                return self.keyword_to_category[word]
        
        # Amount-based categorization for common patterns
        if amount is not None:
            # Large positive amounts are likely income
            if amount > 1000:
                return 'Income'
            
            # Very small amounts might be fees
            if abs(amount) < 5:
                return 'Other'
        
        return 'Other'
    
    def categorize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize all transactions in a DataFrame"""
        if 'Category' not in df.columns:
            df['Category'] = ''
        
        # Only categorize uncategorized transactions
        uncategorized_mask = (df['Category'].isna()) | (df['Category'] == '') | (df['Category'] == 'Other')
        
        for idx in df[uncategorized_mask].index:
            description = df.loc[idx, 'Description']
            amount = df.loc[idx, 'Amount'] if 'Amount' in df.columns else None
            category = self.categorize_transaction(description, amount)
            df.loc[idx, 'Category'] = category
        
        return df
    
    def get_category_stats(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Get statistics for each category"""
        if 'Category' not in df.columns:
            return {}
        
        stats = {}
        
        for category in self.categories.keys():
            category_data = df[df['Category'] == category]
            
            if len(category_data) > 0:
                total_amount = category_data['Amount'].sum()
                transaction_count = len(category_data)
                
                # Determine if it's income or expense
                if category == 'Income':
                    income_amount = total_amount
                    expense_amount = 0
                else:
                    income_amount = category_data[category_data['Amount'] > 0]['Amount'].sum()
                    expense_amount = abs(category_data[category_data['Amount'] < 0]['Amount'].sum())
                
                stats[category] = {
                    'count': transaction_count,
                    'total_amount': total_amount,
                    'income_amount': income_amount,
                    'expense_amount': expense_amount,
                    'color': self.categories[category]['color']
                }
        
        return stats
    
    def bulk_categorize(self, df: pd.DataFrame, category: str, indices: List[int]) -> pd.DataFrame:
        """Bulk categorize selected transactions"""
        if category not in self.categories:
            raise ValueError(f"Unknown category: {category}")
        
        df.loc[indices, 'Category'] = category
        return df
    
    def get_suggestions(self, description: str, current_category: str = None) -> List[Tuple[str, float]]:
        """Get category suggestions for a description with confidence scores"""
        if not description:
            return []
        
        suggestions = []
        desc_lower = description.lower()
        
        for category, data in self.categories.items():
            if category == 'Other':
                continue
            
            confidence = 0
            keyword_matches = 0
            
            for keyword in data['keywords']:
                if keyword in desc_lower:
                    # Exact match gets higher confidence
                    if keyword == desc_lower:
                        confidence += 1.0
                    else:
                        confidence += 0.8
                    keyword_matches += 1
            
            # Partial word matches
            words = desc_lower.split()
            for word in words:
                for keyword in data['keywords']:
                    if word in keyword or keyword in word:
                        confidence += 0.3
            
            # Normalize confidence
            if keyword_matches > 0:
                confidence = min(confidence / keyword_matches, 1.0)
                
                if confidence > 0.2:  # Only suggest if confidence > 20%
                    suggestions.append((category, confidence))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:3]  # Return top 3 suggestions
    
    def add_custom_category(self, name: str, keywords: List[str], color: str = '#6c757d'):
        """Add a custom category"""
        self.categories[name] = {
            'keywords': keywords,
            'color': color
        }
        
        # Update keyword lookup
        for keyword in keywords:
            self.keyword_to_category[keyword.lower()] = name
    
    def get_category_colors(self) -> Dict[str, str]:
        """Get color mapping for all categories"""
        return {cat: data['color'] for cat, data in self.categories.items()}
    
    def get_progress_stats(self, df: pd.DataFrame) -> Dict[str, any]:
        """Get categorization progress statistics"""
        if 'Category' not in df.columns:
            return {
                'total_transactions': len(df),
                'categorized': 0,
                'uncategorized': len(df),
                'progress_percentage': 0
            }
        
        total = len(df)
        uncategorized = len(df[(df['Category'].isna()) | (df['Category'] == '')])
        categorized = total - uncategorized
        
        return {
            'total_transactions': total,
            'categorized': categorized,
            'uncategorized': uncategorized,
            'progress_percentage': (categorized / total * 100) if total > 0 else 0
        }

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function to categorize transactions"""
    engine = CategoryEngine()
    return engine.categorize_dataframe(df)

def get_category_suggestions(description: str) -> List[Tuple[str, float]]:
    """Convenience function to get category suggestions"""
    engine = CategoryEngine()
    return engine.get_suggestions(description)

