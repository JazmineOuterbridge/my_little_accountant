"""
Export Utilities Module
Handles exporting data to CSV, Excel, and PDF formats
"""

import pandas as pd
import os
import zipfile
import json
from datetime import datetime
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

class ExportManager:
    """Handles exporting financial data to various formats"""
    
    def __init__(self):
        self.default_style = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.default_style['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.default_style['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to CSV file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Export with proper formatting
            df.to_csv(filename, index=False, encoding='utf-8')
            return filename
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise Exception(f"Failed to export CSV: {str(e)}")
    
    def export_to_excel(self, df: pd.DataFrame, filename: str, sheet_name: str = "Transactions") -> str:
        """Export DataFrame to Excel file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return filename
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise Exception(f"Failed to export Excel: {str(e)}")
    
    def create_monthly_summary(self, df: pd.DataFrame, year: int, month: int) -> Dict:
        """Create monthly summary statistics"""
        if 'Date' not in df.columns:
            return {}
        
        # Filter data for the month
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        month_data = df[
            (df['Date'].dt.year == year) & 
            (df['Date'].dt.month == month)
        ].copy()
        
        if len(month_data) == 0:
            return {}
        
        # Calculate summary
        income = month_data[month_data['Amount'] > 0]['Amount'].sum()
        expenses = abs(month_data[month_data['Amount'] < 0]['Amount'].sum())
        net = income - expenses
        
        # Category breakdown
        category_stats = {}
        if 'Category' in month_data.columns:
            for category in month_data['Category'].unique():
                if pd.isna(category):
                    continue
                cat_data = month_data[month_data['Category'] == category]
                cat_income = cat_data[cat_data['Amount'] > 0]['Amount'].sum()
                cat_expenses = abs(cat_data[cat_data['Amount'] < 0]['Amount'].sum())
                
                category_stats[category] = {
                    'income': cat_income,
                    'expenses': cat_expenses,
                    'net': cat_income - cat_expenses,
                    'count': len(cat_data)
                }
        
        return {
            'year': year,
            'month': month,
            'total_income': income,
            'total_expenses': expenses,
            'net_flow': net,
            'transaction_count': len(month_data),
            'category_stats': category_stats
        }
    
    def create_pdf_report(self, df: pd.DataFrame, filename: str, title: str = "Financial Report") -> str:
        """Create PDF report with charts and summary"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Title
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 12))
            
            # Summary statistics
            if len(df) > 0:
                income = df[df['Amount'] > 0]['Amount'].sum()
                expenses = abs(df[df['Amount'] < 0]['Amount'].sum())
                net = income - expenses
                
                summary_data = [
                    ['Metric', 'Amount'],
                    ['Total Income', f"${income:,.2f}"],
                    ['Total Expenses', f"${expenses:,.2f}"],
                    ['Net Cash Flow', f"${net:,.2f}"],
                    ['Total Transactions', str(len(df))]
                ]
                
                summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(Paragraph("Summary", self.heading_style))
                story.append(summary_table)
                story.append(Spacer(1, 12))
            
            # Category breakdown
            if 'Category' in df.columns and len(df) > 0:
                category_stats = {}
                for category in df['Category'].unique():
                    if pd.isna(category):
                        continue
                    cat_data = df[df['Category'] == category]
                    cat_income = cat_data[cat_data['Amount'] > 0]['Amount'].sum()
                    cat_expenses = abs(cat_data[cat_data['Amount'] < 0]['Amount'].sum())
                    category_stats[category] = cat_income - cat_expenses
                
                if category_stats:
                    # Sort by amount
                    sorted_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
                    
                    cat_data = [['Category', 'Net Amount', 'Transaction Count']]
                    for category, amount in sorted_categories:
                        count = len(df[df['Category'] == category])
                        cat_data.append([category, f"${amount:,.2f}", str(count)])
                    
                    cat_table = Table(cat_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                    cat_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(Paragraph("Category Breakdown", self.heading_style))
                    story.append(cat_table)
                    story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            return filename
            
        except Exception as e:
            logger.error(f"Error creating PDF report: {e}")
            raise Exception(f"Failed to create PDF report: {str(e)}")
    
    def create_backup(self, df: pd.DataFrame, metadata: Dict, backup_dir: str) -> str:
        """Create timestamped backup with all data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"financial_backup_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Ensure directory exists
            os.makedirs(backup_dir, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main data file
                csv_filename = f"transactions_{timestamp}.csv"
                csv_path = os.path.join(backup_dir, csv_filename)
                df.to_csv(csv_path, index=False)
                zipf.write(csv_path, csv_filename)
                os.remove(csv_path)  # Clean up temp file
                
                # Add metadata
                metadata_filename = f"metadata_{timestamp}.json"
                metadata_path = os.path.join(backup_dir, metadata_filename)
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
                zipf.write(metadata_path, metadata_filename)
                os.remove(metadata_path)  # Clean up temp file
                
                # Add Excel version
                excel_filename = f"transactions_{timestamp}.xlsx"
                excel_path = os.path.join(backup_dir, excel_filename)
                self.export_to_excel(df, excel_path)
                zipf.write(excel_path, excel_filename)
                os.remove(excel_path)  # Clean up temp file
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise Exception(f"Failed to create backup: {str(e)}")
    
    def auto_save(self, df: pd.DataFrame, metadata: Dict, save_path: str) -> str:
        """Auto-save current state to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Prepare data for JSON serialization
            save_data = {
                'transactions': df.to_dict('records'),
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to JSON
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, default=str)
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error auto-saving: {e}")
            raise Exception(f"Failed to auto-save: {str(e)}")
    
    def load_auto_save(self, save_path: str) -> Tuple[pd.DataFrame, Dict]:
        """Load auto-saved data"""
        try:
            if not os.path.exists(save_path):
                return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category']), {}
            
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data['transactions'])
            metadata = data.get('metadata', {})
            
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error loading auto-save: {e}")
            return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category']), {}

def export_transactions_csv(df: pd.DataFrame, filename: str) -> str:
    """Convenience function to export transactions to CSV"""
    exporter = ExportManager()
    return exporter.export_to_csv(df, filename)

def export_transactions_excel(df: pd.DataFrame, filename: str) -> str:
    """Convenience function to export transactions to Excel"""
    exporter = ExportManager()
    return exporter.export_to_excel(df, filename)

def create_financial_report_pdf(df: pd.DataFrame, filename: str, title: str = "Financial Report") -> str:
    """Convenience function to create PDF report"""
    exporter = ExportManager()
    return exporter.create_pdf_report(df, filename, title)

