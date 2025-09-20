"""
My Little Accountant - Personal Finance Management App
A user-friendly web application for managing personal finances with zero coding experience required
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import tempfile
import time
from datetime import datetime, timedelta
import json

# Import our custom modules
from pdf_processor import process_pdf_file, process_pdf_files
from data_cleaner import clean_transaction_data, validate_transaction_data
from category_engine import CategoryEngine, categorize_transactions, get_category_suggestions
from export_utils import ExportManager

# Configure Streamlit page
st.set_page_config(
    page_title="My Little Accountant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .upload-area {
        border: 2px dashed #1f77b4;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .category-income { color: #28a745; }
    .category-expense { color: #dc3545; }
    .category-neutral { color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category'])
if 'category_engine' not in st.session_state:
    st.session_state.category_engine = CategoryEngine()
if 'export_manager' not in st.session_state:
    st.session_state.export_manager = ExportManager()
if 'app_started' not in st.session_state:
    st.session_state.app_started = False
if 'help_shown' not in st.session_state:
    st.session_state.help_shown = False

def load_sample_data():
    """Load sample data for demonstration"""
    sample_data = {
        'Date': [
            '2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
            '2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24'
        ],
        'Description': [
            'Salary Deposit', 'Grocery Store', 'Gas Station', 'Netflix Subscription',
            'Restaurant Dinner', 'Electric Bill', 'Coffee Shop', 'Amazon Purchase',
            'Uber Ride', 'Phone Bill'
        ],
        'Amount': [3000.00, -85.50, -45.20, -15.99, -67.80, -120.45, -4.50, -89.99, -12.75, -65.00],
        'Category': ['Income', 'Food & Dining', 'Transportation', 'Entertainment', 
                   'Food & Dining', 'Utilities', 'Food & Dining', 'Shopping', 
                   'Transportation', 'Utilities']
    }
    return pd.DataFrame(sample_data)

def show_welcome_tour():
    """Show welcome tour for first-time users"""
    if not st.session_state.help_shown:
        with st.expander("🎉 Welcome to My Little Accountant!", expanded=True):
            st.markdown("""
            **Getting Started (3 easy steps):**
            
            1. **📁 Upload Your Bank Statements** - Drag and drop CSV, Excel, or PDF files
            2. **🏷️ Categorize Transactions** - Review and assign categories to your transactions  
            3. **📊 View Your Finances** - See charts and insights about your spending
            
            **💡 Tips:**
            - The app automatically categorizes most transactions for you
            - PDF bank statements are automatically converted to readable data
            - Your data is saved automatically every 30 seconds
            - Click the ❓ icons for help on any section
            
            Ready to get started? Close this panel and upload your first bank statement!
            """)
            if st.button("Got it! Let's start", key="welcome_ok"):
                st.session_state.help_shown = True
                st.rerun()

def process_uploaded_files(uploaded_files):
    """Process uploaded files and return combined DataFrame"""
    all_data = []
    pdf_files = []
    csv_files = []
    excel_files = []
    
    # Separate files by type
    for uploaded_file in uploaded_files:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == 'pdf':
            pdf_files.append(uploaded_file)
        elif file_extension == 'csv':
            csv_files.append(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            excel_files.append(uploaded_file)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    
    # Process CSV files
    for i, uploaded_file in enumerate(csv_files):
        status_text.text(f"Processing CSV file: {uploaded_file.name}")
        try:
            df = pd.read_csv(uploaded_file)
            # Standardize column names
            df.columns = df.columns.str.title()
            if 'Date' in df.columns and 'Description' in df.columns and 'Amount' in df.columns:
                all_data.append(df[['Date', 'Description', 'Amount']])
            else:
                st.warning(f"⚠️ {uploaded_file.name} doesn't have the expected columns (Date, Description, Amount)")
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        progress_bar.progress((i + 1) / total_files)
    
    # Process Excel files
    for i, uploaded_file in enumerate(excel_files):
        status_text.text(f"Processing Excel file: {uploaded_file.name}")
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.title()
            if 'Date' in df.columns and 'Description' in df.columns and 'Amount' in df.columns:
                all_data.append(df[['Date', 'Description', 'Amount']])
            else:
                st.warning(f"⚠️ {uploaded_file.name} doesn't have the expected columns (Date, Description, Amount)")
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
        progress_bar.progress((len(csv_files) + i + 1) / total_files)
    
    # Process PDF files
    if pdf_files:
        status_text.text("Processing PDF files...")
        try:
            # Save PDFs to temporary files
            temp_pdf_paths = []
            for uploaded_file in pdf_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_pdf_paths.append(tmp_file.name)
            
            # Process PDFs
            def progress_callback(message):
                status_text.text(message)
            
            pdf_df = process_pdf_files(temp_pdf_paths, progress_callback)
            if not pdf_df.empty:
                all_data.append(pdf_df)
            
            # Clean up temporary files
            for temp_path in temp_pdf_paths:
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            st.error(f"❌ Error processing PDF files: {str(e)}")
        
        progress_bar.progress(1.0)
    
    # Combine all data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Clean the data
        status_text.text("Cleaning and validating data...")
        cleaned_df, issues = clean_transaction_data(combined_df)
        
        # Show data quality report
        if issues:
            with st.expander("📋 Data Quality Report", expanded=True):
                st.markdown("**Issues Found:**")
                for issue_type, indices in issues.items():
                    if indices:
                        st.warning(f"⚠️ {issue_type.replace('_', ' ').title()}: {len(indices)} transactions")
        
        # Auto-categorize
        status_text.text("Auto-categorizing transactions...")
        categorized_df = categorize_transactions(cleaned_df)
        
        status_text.text("✅ Processing complete!")
        progress_bar.progress(1.0)
        time.sleep(1)
        
        return categorized_df
    
    return pd.DataFrame(columns=['Date', 'Description', 'Amount', 'Category'])

def display_transaction_table(df):
    """Display transaction table with categorization interface"""
    if df.empty:
        st.info("📝 No transactions to display. Upload some bank statements to get started!")
        return
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search transactions", placeholder="Search by description...")
    
    with col2:
        category_filter = st.selectbox(
            "Filter by category",
            ["All Categories"] + list(st.session_state.category_engine.categories.keys())
        )
    
    with col3:
        show_uncategorized = st.checkbox("Show uncategorized only", value=False)
    
    # Apply filters
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Description'].str.contains(search_term, case=False, na=False)]
    
    if category_filter != "All Categories":
        filtered_df = filtered_df[filtered_df['Category'] == category_filter]
    
    if show_uncategorized:
        filtered_df = filtered_df[(filtered_df['Category'].isna()) | (filtered_df['Category'] == '') | (filtered_df['Category'] == 'Other')]
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} transactions**")
    
    # Bulk categorization
    if len(filtered_df) > 0:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            select_all = st.checkbox("Select all showing transactions")
        
        with col2:
            bulk_category = st.selectbox(
                "Bulk assign category",
                [""] + list(st.session_state.category_engine.categories.keys())
            )
        
        with col3:
            if st.button("Apply to Selected", disabled=not bulk_category):
                if select_all:
                    indices = filtered_df.index.tolist()
                    st.session_state.transactions.loc[indices, 'Category'] = bulk_category
                    st.success(f"✅ Assigned '{bulk_category}' to {len(indices)} transactions")
                    st.rerun()
    
    # Display table
    if len(filtered_df) > 0:
        # Create editable table
        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "Date": st.column_config.DateColumn(
                    "Date",
                    help="Transaction date",
                    format="YYYY-MM-DD"
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    help="Transaction description",
                    width="large"
                ),
                "Amount": st.column_config.NumberColumn(
                    "Amount",
                    help="Transaction amount",
                    format="$%.2f"
                ),
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    help="Transaction category",
                    options=list(st.session_state.category_engine.categories.keys()),
                    required=True
                )
            },
            hide_index=True,
            use_container_width=True,
            key="transaction_editor"
        )
        
        # Update session state with changes
        if not edited_df.equals(filtered_df):
            for idx in edited_df.index:
                if idx in filtered_df.index:
                    st.session_state.transactions.loc[idx] = edited_df.loc[idx]
    
    # Progress indicator
    progress_stats = st.session_state.category_engine.get_progress_stats(df)
    progress_percentage = progress_stats['progress_percentage']
    
    st.markdown(f"**Categorization Progress: {progress_percentage:.1f}% ({progress_stats['categorized']}/{progress_stats['total_transactions']})**")
    st.progress(progress_percentage / 100)

def display_dashboard(df):
    """Display financial dashboard with charts"""
    if df.empty:
        st.info("📊 Upload and categorize transactions to see your financial dashboard!")
        return
    
    # Calculate summary metrics
    validation = validate_transaction_data(df)
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Income",
            value=f"${validation.get('total_income', 0):,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"${validation.get('total_expenses', 0):,.2f}",
            delta=None
        )
    
    with col3:
        net_flow = validation.get('net_flow', 0)
        st.metric(
            label="📈 Net Cash Flow",
            value=f"${net_flow:,.2f}",
            delta=f"${net_flow:,.2f}" if net_flow != 0 else None
        )
    
    with col4:
        progress_stats = st.session_state.category_engine.get_progress_stats(df)
        st.metric(
            label="✅ Categorized",
            value=f"{progress_stats['categorized']}/{progress_stats['total_transactions']}",
            delta=f"{progress_stats['progress_percentage']:.1f}%"
        )
    
    st.markdown("---")
    
    # Time period selector
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            years = sorted(df['Date'].dt.year.dropna().unique())
            selected_year = st.selectbox("Select Year", years, index=len(years)-1 if years else 0)
            
            # Filter by year
            yearly_df = df[df['Date'].dt.year == selected_year]
        else:
            yearly_df = df
    
    with col2:
        if len(yearly_df) > 0:
            months = sorted(yearly_df['Date'].dt.month.dropna().unique())
            month_names = [datetime(1, m, 1).strftime('%B') for m in months]
            selected_month = st.selectbox("Select Month", month_names, index=len(month_names)-1 if month_names else 0)
            
            # Filter by month
            monthly_df = yearly_df[yearly_df['Date'].dt.month == months[month_names.index(selected_month)] if month_names else 0]
        else:
            monthly_df = yearly_df
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Category breakdown (pie chart)
        if len(monthly_df) > 0 and 'Category' in monthly_df.columns:
            category_stats = st.session_state.category_engine.get_category_stats(monthly_df)
            
            if category_stats:
                categories = list(category_stats.keys())
                amounts = [abs(stats['expense_amount']) for stats in category_stats.values()]
                
                fig_pie = px.pie(
                    values=amounts,
                    names=categories,
                    title=f"Spending by Category - {selected_month} {selected_year}",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Monthly trend (line chart)
        if len(yearly_df) > 0:
            # Group by month
            monthly_summary = yearly_df.groupby(yearly_df['Date'].dt.month).agg({
                'Amount': ['sum', 'count']
            }).round(2)
            
            monthly_summary.columns = ['Net_Flow', 'Transaction_Count']
            monthly_summary.index = [datetime(1, m, 1).strftime('%B') for m in monthly_summary.index]
            
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=monthly_summary.index,
                y=monthly_summary['Net_Flow'],
                mode='lines+markers',
                name='Net Cash Flow',
                line=dict(color='#1f77b4', width=3)
            ))
            
            fig_line.update_layout(
                title=f"Monthly Cash Flow - {selected_year}",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
    
    # Category breakdown table
    if len(monthly_df) > 0 and 'Category' in monthly_df.columns:
        st.markdown("### 📋 Category Breakdown")
        category_stats = st.session_state.category_engine.get_category_stats(monthly_df)
        
        if category_stats:
            category_data = []
            for category, stats in category_stats.items():
                category_data.append({
                    'Category': category,
                    'Transactions': stats['count'],
                    'Income': f"${stats['income_amount']:,.2f}",
                    'Expenses': f"${stats['expense_amount']:,.2f}",
                    'Net': f"${stats['total_amount']:,.2f}"
                })
            
            category_df = pd.DataFrame(category_data)
            st.dataframe(category_df, use_container_width=True, hide_index=True)

def auto_save_data():
    """Auto-save data every 30 seconds"""
    if not st.session_state.transactions.empty:
        try:
            save_path = "my_finances.json"
            metadata = {
                'last_saved': datetime.now().isoformat(),
                'total_transactions': len(st.session_state.transactions)
            }
            st.session_state.export_manager.auto_save(
                st.session_state.transactions, 
                metadata, 
                save_path
            )
        except Exception as e:
            st.error(f"Auto-save failed: {str(e)}")

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">💰 My Little Accountant</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Your Personal Finance Assistant - Zero Coding Required!</p>', unsafe_allow_html=True)
    
    # Welcome tour for new users
    show_welcome_tour()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("📁 Load Sample Data", help="Load sample transactions to try the app"):
            st.session_state.transactions = load_sample_data()
            st.success("✅ Sample data loaded!")
            st.rerun()
        
        if st.button("💾 Export Data", help="Download your categorized transactions"):
            if not st.session_state.transactions.empty:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                col1, col2 = st.columns(2)
                with col1:
                    csv_data = st.session_state.transactions.to_csv(index=False)
                    st.download_button(
                        label="📄 CSV",
                        data=csv_data,
                        file_name=f"transactions_{timestamp}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    try:
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                            excel_path = tmp_file.name
                        
                        st.session_state.export_manager.export_to_excel(
                            st.session_state.transactions, 
                            excel_path
                        )
                        
                        with open(excel_path, 'rb') as f:
                            excel_data = f.read()
                        
                        st.download_button(
                            label="📊 Excel",
                            data=excel_data,
                            file_name=f"transactions_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # Clean up temporary file
                        try:
                            os.unlink(excel_path)
                        except:
                            pass
                            
                    except Exception as e:
                        st.error(f"Could not create Excel export: {str(e)}")
                        st.info("CSV export is still available.")
            else:
                st.warning("No data to export")
        
        if st.button("🔄 Create Backup", help="Create a complete backup of all your data"):
            if not st.session_state.transactions.empty:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = st.session_state.export_manager.create_backup(
                        st.session_state.transactions,
                        {'created': datetime.now().isoformat()},
                        "backups"
                    )
                    
                    with open(backup_path, 'rb') as f:
                        st.download_button(
                            label="💾 Download Backup",
                            data=f.read(),
                            file_name=f"financial_backup_{timestamp}.zip",
                            mime="application/zip"
                        )
                    
                    st.success("✅ Backup created!")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")
            else:
                st.warning("No data to backup")
        
        st.markdown("---")
        
        # Help section
        with st.expander("❓ Help & Support"):
            st.markdown("""
            **Common Issues:**
            
            **PDF not working?** 
            - Make sure it's a bank statement PDF
            - Try converting to CSV first
            - Check if the PDF is password protected
            
            **Wrong categories?**
            - Use the bulk categorization feature
            - Categories improve with more data
            
            **Data not saving?**
            - Data saves automatically every 30 seconds
            - Check if you have write permissions
            - Try creating a manual backup
            
            **Need more help?**
            - Check the sample data for expected format
            - Look for ❓ icons throughout the app
            """)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📁 Upload Data", "🏷️ Categorize", "📊 Dashboard"])
    
    with tab1:
        st.markdown("### 📁 Upload Your Bank Statements")
        
        # File upload area
        st.markdown("""
        <div class="upload-area">
            <h3>📄 Drop your bank statements here</h3>
            <p>Supports CSV, Excel (.xlsx), and PDF files</p>
            <p><small>Expected columns: Date, Description, Amount</small></p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['csv', 'xlsx', 'xls', 'pdf'],
            help="Upload multiple files at once for batch processing"
        )
        
        if uploaded_files:
            if st.button("🔄 Process Files", type="primary"):
                with st.spinner("Processing files..."):
                    processed_df = process_uploaded_files(uploaded_files)
                    if not processed_df.empty:
                        st.session_state.transactions = processed_df
                        st.success(f"✅ Successfully processed {len(processed_df)} transactions!")
                        st.rerun()
                    else:
                        st.error("❌ No valid transactions found in the uploaded files")
        
        # Sample files section
        with st.expander("📋 Download Sample Files", expanded=False):
            st.markdown("**Try these sample files to see the expected format:**")
            
            # Create sample CSV
            sample_df = load_sample_data()
            csv_sample = sample_df.to_csv(index=False)
            st.download_button(
                label="📄 Download Sample CSV",
                data=csv_sample,
                file_name="sample_transactions.csv",
                mime="text/csv"
            )
            
            # Create sample Excel
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                    excel_path = tmp_file.name
                
                st.session_state.export_manager.export_to_excel(sample_df, excel_path)
                
                with open(excel_path, 'rb') as f:
                    excel_data = f.read()
                
                st.download_button(
                    label="📊 Download Sample Excel",
                    data=excel_data,
                    file_name="sample_transactions.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Clean up temporary file
                import os
                try:
                    os.unlink(excel_path)
                except:
                    pass
                    
            except Exception as e:
                st.error(f"Could not create sample Excel file: {str(e)}")
                st.info("You can still download the CSV sample file above.")
    
    with tab2:
        st.markdown("### 🏷️ Categorize Your Transactions")
        st.markdown("Review and assign categories to your transactions. Most transactions are auto-categorized!")
        
        display_transaction_table(st.session_state.transactions)
    
    with tab3:
        st.markdown("### 📊 Financial Dashboard")
        st.markdown("Visualize your spending patterns and financial health")
        
        display_dashboard(st.session_state.transactions)
    
    # Auto-save every 30 seconds
    if st.session_state.transactions is not None and not st.session_state.transactions.empty:
        auto_save_data()

if __name__ == "__main__":
    main()

