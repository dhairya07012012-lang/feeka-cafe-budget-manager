import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
from datetime import datetime
import json
import os
import pytz

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Feeka Cafe Budget Manager",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== THEME MANAGEMENT ====================
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'

# Theme Colors
if st.session_state.theme == 'dark':
    bg_color = "#1E1E1E"
    text_color = "#FFFFFF"
    card_bg = "#2D2D2D"
    accent_color = "#FF6B6B"
    secondary_color = "#4ECDC4"
else:
    bg_color = "#FFFFFF"
    text_color = "#262730"
    card_bg = "#F0F2F6"
    accent_color = "#FF6B6B"
    secondary_color = "#4ECDC4"

# ==================== CUSTOM CSS ====================
st.markdown(f"""
<style>
    /* Main Theme */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Header Styles */
    .main-header {{
        font-size: 2.5rem;
        color: {accent_color};
        text-align: center;
        padding: 0.5rem;
        font-weight: bold;
    }}
    
    .sub-header {{
        font-size: 1.5rem;
        color: {secondary_color};
        padding: 0.5rem 0;
        border-bottom: 2px solid {secondary_color};
        margin-bottom: 1rem;
    }}
    
    /* Date Time Display */
    .datetime-display {{
        position: fixed;
        top: 60px;
        right: 20px;
        font-size: 0.75rem;
        color: {text_color};
        opacity: 0.7;
        text-align: right;
        z-index: 999;
        background-color: {bg_color};
        padding: 5px 10px;
        border-radius: 5px;
    }}
    
    /* Card Styles */
    .metric-card {{
        background-color: {card_bg};
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid {accent_color};
        margin: 0.5rem 0;
    }}
    
    /* Theme Toggle */
    .theme-toggle {{
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 999;
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: {card_bg};
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Data Editor Styling */
    .stDataFrame {{
        background-color: {card_bg};
    }}
    
    /* Button Styling */
    .stButton > button {{
        border-radius: 8px;
        font-weight: 500;
    }}
    
    /* Expander Styling */
    .streamlit-expanderHeader {{
        background-color: {card_bg};
        border-radius: 8px;
    }}
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_bg};
        border-radius: 8px;
        padding: 8px 16px;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== DATE TIME DISPLAY ====================
# Get current time in IST (Indian Standard Time) - Change timezone as needed
try:
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
except:
    current_time = datetime.now()

date_str = current_time.strftime("%A, %d %B %Y")
time_str = current_time.strftime("%I:%M:%S %p")

st.markdown(f"""
<div class="datetime-display">
    <div>{date_str}</div>
    <div>{time_str}</div>
</div>
""", unsafe_allow_html=True)

# ==================== DATA STORAGE FUNCTIONS ====================
DATA_DIR = "feeka_data"
REVENUE_FILE = os.path.join(DATA_DIR, "revenue_data.json")
EXPENSE_FILE = os.path.join(DATA_DIR, "expense_data.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def ensure_data_directory():
    """Create data directory if not exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_revenue(df):
    """Save revenue data to JSON"""
    try:
        ensure_data_directory()
        df_copy = df.copy()
        df_copy['Date'] = df_copy['Date'].astype(str)
        df_copy.to_json(REVENUE_FILE, orient='records', indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving revenue: {e}")
        return False

def load_revenue():
    """Load revenue data from JSON"""
    ensure_data_directory()
    if os.path.exists(REVENUE_FILE):
        try:
            df = pd.read_json(REVENUE_FILE)
            if len(df) > 0:
                df['Date'] = pd.to_datetime(df['Date'])
                return df
        except:
            pass
    return get_default_revenue()

def save_expenses(df):
    """Save expense data to JSON"""
    try:
        ensure_data_directory()
        df_copy = df.copy()
        df_copy['Date'] = df_copy['Date'].astype(str)
        df_copy.to_json(EXPENSE_FILE, orient='records', indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving expenses: {e}")
        return False

def load_expenses():
    """Load expense data from JSON"""
    ensure_data_directory()
    if os.path.exists(EXPENSE_FILE):
        try:
            df = pd.read_json(EXPENSE_FILE)
            if len(df) > 0:
                df['Date'] = pd.to_datetime(df['Date'])
                return df
        except:
            pass
    return get_default_expenses()

def get_default_revenue():
    """Create default revenue data"""
    dates = pd.date_range(start='2024-01-01', periods=12, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Source': ['Dine-in', 'Takeaway', 'Delivery', 'Dine-in', 'Takeaway',
                   'Dine-in', 'Delivery', 'Catering', 'Dine-in', 'Takeaway',
                   'Delivery', 'Dine-in'],
        'Description': ['Lunch service', 'Coffee orders', 'Food delivery', 'Dinner service',
                       'Snacks', 'Weekend brunch', 'Online orders', 'Office party',
                       'Regular customers', 'Morning rush', 'Evening orders', 'Full day'],
        'Amount': [4500, 2200, 1800, 5200, 1500, 6800, 2100, 8500, 4800, 1900, 2300, 5500]
    })

def get_default_expenses():
    """Create default expense data"""
    dates = pd.date_range(start='2024-01-01', periods=12, freq='D')
    return pd.DataFrame({
        'Date': dates,
        'Category': ['Ingredients', 'Rent', 'Salaries', 'Utilities', 'Ingredients',
                     'Marketing', 'Maintenance', 'Ingredients', 'Supplies', 'Utilities',
                     'Ingredients', 'Insurance'],
        'Description': ['Fresh vegetables & fruits', 'Monthly rent', 'Staff salaries', 'Electricity',
                       'Coffee beans & milk', 'Social media ads', 'AC repair', 'Meat & seafood',
                       'Cleaning supplies', 'Water bill', 'Bakery items', 'Annual premium'],
        'Amount': [2500, 15000, 25000, 3500, 4000, 2000, 1500, 3500, 800, 1200, 2800, 5000]
    })

# ==================== INITIALIZE DATA ====================
if 'revenue' not in st.session_state:
    st.session_state.revenue = load_revenue()

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_expenses()

if 'advice_history' not in st.session_state:
    st.session_state.advice_history = []

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo and Title
    st.markdown("## 🍽️ Feeka Cafe")
    st.markdown("---")
    
    # Theme Toggle
    st.markdown("### 🎨 Theme")
    theme_label = "🌙 Dark Mode" if st.session_state.theme == 'light' else "☀️ Light Mode"
    if st.button(theme_label, use_container_width=True):
        toggle_theme()
        st.rerun()
    
    st.markdown("---")
    
    # API Key Input
    st.markdown("### 🔑 API Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    
    if api_key:
        st.success("✅ API Key entered")
    else:
        st.warning("⚠️ Enter API key for AI features")
    
    st.markdown("---")
    
    # Data Management
    st.markdown("### 💾 Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save", use_container_width=True):
            if save_revenue(st.session_state.revenue) and save_expenses(st.session_state.expenses):
                st.success("✅ Saved!")
    
    with col2:
        if st.button("🔄 Reload", use_container_width=True):
            st.session_state.revenue = load_revenue()
            st.session_state.expenses = load_expenses()
            st.success("✅ Reloaded!")
            st.rerun()
    
    # Export Buttons
    st.markdown("#### 📥 Export Data")
    
    revenue_json = st.session_state.revenue.to_json(orient='records', date_format='iso', indent=2)
    st.download_button(
        "📊 Export Revenue",
        revenue_json,
        f"feeka_revenue_{current_time.strftime('%Y%m%d')}.json",
        "application/json",
        use_container_width=True
    )
    
    expense_json = st.session_state.expenses.to_json(orient='records', date_format='iso', indent=2)
    st.download_button(
        "💸 Export Expenses",
        expense_json,
        f"feeka_expenses_{current_time.strftime('%Y%m%d')}.json",
        "application/json",
        use_container_width=True
    )
    
    # Import Section
    st.markdown("#### 📤 Import Data")
    
    uploaded_revenue = st.file_uploader("Import Revenue", type=['json'], key='rev_import')
    if uploaded_revenue:
        try:
            imported = pd.read_json(uploaded_revenue)
            imported['Date'] = pd.to_datetime(imported['Date'])
            st.session_state.revenue = imported
            save_revenue(st.session_state.revenue)
            st.success("✅ Revenue imported!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
    
    uploaded_expense = st.file_uploader("Import Expenses", type=['json'], key='exp_import')
    if uploaded_expense:
        try:
            imported = pd.read_json(uploaded_expense)
            imported['Date'] = pd.to_datetime(imported['Date'])
            st.session_state.expenses = imported
            save_expenses(st.session_state.expenses)
            st.success("✅ Expenses imported!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Reset Data
    st.markdown("### ⚠️ Danger Zone")
    if st.button("🗑️ Reset All Data", type="secondary", use_container_width=True):
        st.session_state.confirm_reset = True
    
    if st.session_state.get('confirm_reset', False):
        st.warning("Are you sure? This will delete all data!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Reset"):
                st.session_state.revenue = get_default_revenue()
                st.session_state.expenses = get_default_expenses()
                save_revenue(st.session_state.revenue)
                save_expenses(st.session_state.expenses)
                st.session_state.confirm_reset = False
                st.success("✅ Data reset!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_reset = False
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown("[Get OpenAI API Key](https://platform.openai.com/api-keys)")
    st.markdown("[OpenAI Billing](https://platform.openai.com/account/billing)")

# ==================== MAIN CONTENT ====================

# Title
st.markdown('<h1 class="main-header">🍽️ Feeka Cafe Budget Manager</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; opacity: 0.8;">Complete Financial Management with AI-Powered Insights</p>', unsafe_allow_html=True)

# Calculate Metrics
total_revenue = st.session_state.revenue['Amount'].sum()
total_expenses = st.session_state.expenses['Amount'].sum()
net_profit = total_revenue - total_expenses
profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Dashboard",
    "📈 Revenue",
    "💸 Expenses",
    "📊 Reports",
    "🤖 AI Advisor"
])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    st.markdown('<h2 class="sub-header">💰 Financial Dashboard</h2>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 Total Revenue",
            value=f"₹{total_revenue:,.0f}",
            delta=f"{len(st.session_state.revenue)} entries"
        )
    
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"₹{total_expenses:,.0f}",
            delta=f"{len(st.session_state.expenses)} entries"
        )
    
    with col3:
        delta_color = "normal" if net_profit >= 0 else "inverse"
        st.metric(
            label="📊 Net Profit",
            value=f"₹{net_profit:,.0f}",
            delta=f"{profit_margin:.1f}%",
            delta_color=delta_color
        )
    
    with col4:
        status = "Healthy ✅" if profit_margin > 15 else ("Warning ⚠️" if profit_margin > 0 else "Loss ❌")
        st.metric(
            label="📈 Status",
            value=status,
            delta=f"{profit_margin:.1f}% margin"
        )
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue vs Expenses")
        fig = go.Figure(data=[
            go.Bar(name='Revenue', x=['Current Period'], y=[total_revenue], 
                   marker_color=secondary_color, text=[f'₹{total_revenue:,.0f}'], textposition='auto'),
            go.Bar(name='Expenses', x=['Current Period'], y=[total_expenses], 
                   marker_color=accent_color, text=[f'₹{total_expenses:,.0f}'], textposition='auto')
        ])
        fig.update_layout(
            barmode='group',
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Expense Distribution")
        expense_by_cat = st.session_state.expenses.groupby('Category')['Amount'].sum()
        fig = px.pie(
            values=expense_by_cat.values,
            names=expense_by_cat.index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue Trend
    st.markdown("---")
    st.subheader("📈 Revenue Trend Over Time")
    
    revenue_trend = st.session_state.revenue.groupby('Date')['Amount'].sum().reset_index()
    revenue_trend = revenue_trend.sort_values('Date')
    
    fig = px.area(
        revenue_trend,
        x='Date',
        y='Amount',
        color_discrete_sequence=[secondary_color]
    )
    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent Activity
    st.markdown("---")
    st.subheader("🕐 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Latest Revenue Entries**")
        recent_rev = st.session_state.revenue.sort_values('Date', ascending=False).head(5)
        recent_rev_display = recent_rev.copy()
        recent_rev_display['Date'] = recent_rev_display['Date'].dt.strftime('%d %b %Y')
        recent_rev_display['Amount'] = recent_rev_display['Amount'].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(recent_rev_display, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Latest Expense Entries**")
        recent_exp = st.session_state.expenses.sort_values('Date', ascending=False).head(5)
        recent_exp_display = recent_exp.copy()
        recent_exp_display['Date'] = recent_exp_display['Date'].dt.strftime('%d %b %Y')
        recent_exp_display['Amount'] = recent_exp_display['Amount'].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(recent_exp_display, use_container_width=True, hide_index=True)

# ==================== TAB 2: REVENUE ====================
with tab2:
    st.markdown('<h2 class="sub-header">📈 Revenue Management</h2>', unsafe_allow_html=True)
    
    # Add Revenue Form
    with st.expander("➕ Add New Revenue Entry", expanded=False):
        with st.form("add_revenue_form", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rev_date = st.date_input("📅 Date", datetime.now())
            with col2:
                rev_source = st.selectbox("📍 Source", 
                    ["Dine-in", "Takeaway", "Delivery", "Catering", "Online Order", "Other"])
            with col3:
                rev_desc = st.text_input("📝 Description", placeholder="e.g., Lunch service")
            with col4:
                rev_amount = st.number_input("💰 Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
            
            submitted = st.form_submit_button("💾 Add Revenue Entry", type="primary", use_container_width=True)
            
            if submitted:
                if rev_amount > 0 and rev_desc:
                    new_entry = pd.DataFrame({
                        'Date': [pd.Timestamp(rev_date)],
                        'Source': [rev_source],
                        'Description': [rev_desc],
                        'Amount': [rev_amount]
                    })
                    st.session_state.revenue = pd.concat([st.session_state.revenue, new_entry], ignore_index=True)
                    save_revenue(st.session_state.revenue)
                    st.success(f"✅ Revenue of ₹{rev_amount:,.2f} added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill in all fields with valid values")
    
    # Revenue Statistics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Revenue", f"₹{total_revenue:,.0f}")
    with col2:
        avg_rev = st.session_state.revenue['Amount'].mean()
        st.metric("📈 Average Entry", f"₹{avg_rev:,.0f}")
    with col3:
        max_rev = st.session_state.revenue['Amount'].max()
        st.metric("🏆 Highest Entry", f"₹{max_rev:,.0f}")
    with col4:
        st.metric("📝 Total Entries", len(st.session_state.revenue))
    
    # Revenue Table with Delete Option
    st.markdown("---")
    st.subheader("📋 All Revenue Entries")
    
    revenue_display = st.session_state.revenue.sort_values('Date', ascending=False).copy()
    revenue_display = revenue_display.reset_index(drop=True)
    revenue_display['Delete'] = False
    
    edited_rev = st.data_editor(
        revenue_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Delete": st.column_config.CheckboxColumn("🗑️ Delete", default=False),
            "Date": st.column_config.DateColumn("📅 Date", format="DD/MM/YYYY"),
            "Source": st.column_config.SelectboxColumn("📍 Source", 
                options=["Dine-in", "Takeaway", "Delivery", "Catering", "Online Order", "Other"]),
            "Description": st.column_config.TextColumn("📝 Description"),
            "Amount": st.column_config.NumberColumn("💰 Amount", format="₹%.2f")
        },
        num_rows="dynamic"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ Delete Selected", type="secondary", key="del_rev"):
            rows_to_keep = edited_rev[edited_rev['Delete'] == False].drop('Delete', axis=1)
            if len(rows_to_keep) < len(st.session_state.revenue):
                deleted_count = len(st.session_state.revenue) - len(rows_to_keep)
                st.session_state.revenue = rows_to_keep.reset_index(drop=True)
                save_revenue(st.session_state.revenue)
                st.success(f"✅ Deleted {deleted_count} entries!")
                st.rerun()
            else:
                st.info("ℹ️ No entries selected for deletion")
    
    # Revenue Charts
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue by Source")
        rev_by_source = st.session_state.revenue.groupby('Source')['Amount'].sum().sort_values(ascending=True)
        fig = px.bar(
            rev_by_source,
            orientation='h',
            color_discrete_sequence=[secondary_color]
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Daily Revenue Trend")
        rev_daily = st.session_state.revenue.groupby('Date')['Amount'].sum().reset_index()
        fig = px.line(
            rev_daily,
            x='Date',
            y='Amount',
            markers=True,
            color_discrete_sequence=[secondary_color]
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: EXPENSES ====================
with tab3:
    st.markdown('<h2 class="sub-header">💸 Expense Management</h2>', unsafe_allow_html=True)
    
    # Add Expense Form
    with st.expander("➕ Add New Expense Entry", expanded=False):
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                exp_date = st.date_input("📅 Date", datetime.now())
                exp_category = st.selectbox("📁 Category",
                    ["Ingredients", "Rent", "Salaries", "Utilities", "Marketing",
                     "Maintenance", "Supplies", "Insurance", "Equipment", "Other"])
            
            with col2:
                exp_desc = st.text_input("📝 Description", placeholder="e.g., Monthly electricity bill")
                exp_amount = st.number_input("💰 Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
            
            submitted = st.form_submit_button("💾 Add Expense Entry", type="primary", use_container_width=True)
            
            if submitted:
                if exp_amount > 0 and exp_desc:
                    new_entry = pd.DataFrame({
                        'Date': [pd.Timestamp(exp_date)],
                        'Category': [exp_category],
                        'Description': [exp_desc],
                        'Amount': [exp_amount]
                    })
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_entry], ignore_index=True)
                    save_expenses(st.session_state.expenses)
                    st.success(f"✅ Expense of ₹{exp_amount:,.2f} added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please fill in all fields with valid values")
    
    # Expense Statistics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💸 Total Expenses", f"₹{total_expenses:,.0f}")
    with col2:
        avg_exp = st.session_state.expenses['Amount'].mean()
        st.metric("📈 Average Entry", f"₹{avg_exp:,.0f}")
    with col3:
        max_exp = st.session_state.expenses['Amount'].max()
        st.metric("⚠️ Highest Entry", f"₹{max_exp:,.0f}")
    with col4:
        st.metric("📝 Total Entries", len(st.session_state.expenses))
    
    # Expense Table with Delete Option
    st.markdown("---")
    st.subheader("📋 All Expense Entries")
    
    expense_display = st.session_state.expenses.sort_values('Date', ascending=False).copy()
    expense_display = expense_display.reset_index(drop=True)
    expense_display['Delete'] = False
    
    edited_exp = st.data_editor(
        expense_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Delete": st.column_config.CheckboxColumn("🗑️ Delete", default=False),
            "Date": st.column_config.DateColumn("📅 Date", format="DD/MM/YYYY"),
            "Category": st.column_config.SelectboxColumn("📁 Category",
                options=["Ingredients", "Rent", "Salaries", "Utilities", "Marketing",
                         "Maintenance", "Supplies", "Insurance", "Equipment", "Other"]),
            "Description": st.column_config.TextColumn("📝 Description"),
            "Amount": st.column_config.NumberColumn("💰 Amount", format="₹%.2f")
        },
        num_rows="dynamic"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🗑️ Delete Selected", type="secondary", key="del_exp"):
            rows_to_keep = edited_exp[edited_exp['Delete'] == False].drop('Delete', axis=1)
            if len(rows_to_keep) < len(st.session_state.expenses):
                deleted_count = len(st.session_state.expenses) - len(rows_to_keep)
                st.session_state.expenses = rows_to_keep.reset_index(drop=True)
                save_expenses(st.session_state.expenses)
                st.success(f"✅ Deleted {deleted_count} entries!")
                st.rerun()
            else:
                st.info("ℹ️ No entries selected for deletion")
    
    # Expense Charts
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Expenses by Category")
        exp_by_cat = st.session_state.expenses.groupby('Category')['Amount'].sum().sort_values(ascending=True)
        fig = px.bar(
            exp_by_cat,
            orientation='h',
            color_discrete_sequence=[accent_color]
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Daily Expense Trend")
        exp_daily = st.session_state.expenses.groupby('Date')['Amount'].sum().reset_index()
        fig = px.line(
            exp_daily,
            x='Date',
            y='Amount',
            markers=True,
            color_discrete_sequence=[accent_color]
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 4: REPORTS ====================
with tab4:
    st.markdown('<h2 class="sub-header">📊 Financial Reports</h2>', unsafe_allow_html=True)
    
    # Date Range Filter
    st.subheader("🗓️ Select Date Range")
    col1, col2 = st.columns(2)
    
    with col1:
        min_date = st.session_state.revenue['Date'].min().date() if len(st.session_state.revenue) > 0 else datetime.now().date()
        start_date = st.date_input("From Date", value=min_date)
    
    with col2:
        max_date = st.session_state.revenue['Date'].max().date() if len(st.session_state.revenue) > 0 else datetime.now().date()
        end_date = st.date_input("To Date", value=max_date)
    
    # Filter Data
    filtered_revenue = st.session_state.revenue[
        (st.session_state.revenue['Date'].dt.date >= start_date) &
        (st.session_state.revenue['Date'].dt.date <= end_date)
    ]
    
    filtered_expenses = st.session_state.expenses[
        (st.session_state.expenses['Date'].dt.date >= start_date) &
        (st.session_state.expenses['Date'].dt.date <= end_date)
    ]
    
    period_revenue = filtered_revenue['Amount'].sum()
    period_expenses = filtered_expenses['Amount'].sum()
    period_profit = period_revenue - period_expenses
    period_margin = (period_profit / period_revenue * 100) if period_revenue > 0 else 0
    
    # Period Metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Period Revenue", f"₹{period_revenue:,.0f}")
    with col2:
        st.metric("💸 Period Expenses", f"₹{period_expenses:,.0f}")
    with col3:
        st.metric("💰 Period Profit", f"₹{period_profit:,.0f}")
    with col4:
        st.metric("📈 Profit Margin", f"{period_margin:.1f}%")
    
    # P&L Statement
    st.markdown("---")
    st.subheader("📄 Profit & Loss Statement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💵 Revenue")
        if len(filtered_revenue) > 0:
            rev_by_source = filtered_revenue.groupby('Source')['Amount'].sum()
            for source, amount in rev_by_source.items():
                st.markdown(f"- **{source}:** ₹{amount:,.0f}")
        else:
            st.info("No revenue data for selected period")
        st.markdown(f"**Total Revenue: ₹{period_revenue:,.0f}**")
    
    with col2:
        st.markdown("### 💸 Expenses")
        if len(filtered_expenses) > 0:
            exp_by_cat = filtered_expenses.groupby('Category')['Amount'].sum()
            for category, amount in exp_by_cat.items():
                st.markdown(f"- **{category}:** ₹{amount:,.0f}")
        else:
            st.info("No expense data for selected period")
        st.markdown(f"**Total Expenses: ₹{period_expenses:,.0f}**")
    
    # Summary Box
    st.markdown("---")
    profit_color = "green" if period_profit >= 0 else "red"
    st.markdown(f"""
    <div style="background-color: {card_bg}; padding: 20px; border-radius: 10px; border-left: 5px solid {profit_color};">
        <h3 style="color: {text_color};">📊 Summary for {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}</h3>
        <p style="font-size: 1.2rem; color: {text_color};">Net Profit: <strong style="color: {profit_color};">₹{period_profit:,.0f}</strong></p>
        <p style="font-size: 1.2rem; color: {text_color};">Profit Margin: <strong style="color: {profit_color};">{period_margin:.1f}%</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Download Reports
    st.markdown("---")
    st.subheader("📥 Download Reports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(filtered_revenue) > 0:
            rev_csv = filtered_revenue.to_csv(index=False)
            st.download_button(
                "📊 Revenue CSV",
                rev_csv,
                f"feeka_revenue_{start_date}_{end_date}.csv",
                "text/csv",
                use_container_width=True
            )
    
    with col2:
        if len(filtered_expenses) > 0:
            exp_csv = filtered_expenses.to_csv(index=False)
            st.download_button(
                "💸 Expenses CSV",
                exp_csv,
                f"feeka_expenses_{start_date}_{end_date}.csv",
                "text/csv",
                use_container_width=True
            )
    
    with col3:
        pl_report = f"""
========================================
FEEKA CAFE - PROFIT & LOSS STATEMENT
========================================
Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}
Generated: {current_time.strftime('%d %b %Y %I:%M %p')}
----------------------------------------

REVENUE:
{''.join([f'{source}: ₹{amount:,.0f}' + chr(10) for source, amount in filtered_revenue.groupby('Source')['Amount'].sum().items()]) if len(filtered_revenue) > 0 else 'No data'}
----------------------------------------
TOTAL REVENUE: ₹{period_revenue:,.0f}

EXPENSES:
{''.join([f'{cat}: ₹{amount:,.0f}' + chr(10) for cat, amount in filtered_expenses.groupby('Category')['Amount'].sum().items()]) if len(filtered_expenses) > 0 else 'No data'}
----------------------------------------
TOTAL EXPENSES: ₹{period_expenses:,.0f}

========================================
NET PROFIT: ₹{period_profit:,.0f}
PROFIT MARGIN: {period_margin:.1f}%
========================================
        """
        st.download_button(
            "📄 P&L Statement",
            pl_report,
            f"feeka_pl_{start_date}_{end_date}.txt",
            "text/plain",
            use_container_width=True
        )

# ==================== TAB 5: AI ADVISOR ====================
with tab5:
    st.markdown('<h2 class="sub-header">🤖 AI Finance Advisor</h2>', unsafe_allow_html=True)
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to use the AI Advisor")
        st.markdown("""
        ### 🔑 How to get an API Key:
        1. Go to [OpenAI Platform](https://platform.openai.com/signup)
        2. Create an account or sign in
        3. Go to [API Keys](https://platform.openai.com/api-keys)
        4. Create a new secret key
        5. Add billing at [Billing](https://platform.openai.com/account/billing)
        6. Paste the key in the sidebar
        """)
    else:
        client = OpenAI(api_key=api_key)
        
        st.info("💡 Ask me anything about Feeka Cafe's finances! I'll analyze your actual data and provide personalized advice.")
        
        # Financial Context
        expense_breakdown = st.session_state.expenses.groupby('Category')['Amount'].sum().to_dict()
        revenue_breakdown = st.session_state.revenue.groupby('Source')['Amount'].sum().to_dict()
        
        financial_context = f"""
You are a professional financial advisor for Feeka Cafe, a restaurant/cafe business.

CURRENT FINANCIAL DATA:

REVENUE ANALYSIS:
- Total Revenue: ₹{total_revenue:,.0f}
- Revenue Breakdown by Source: {revenue_breakdown}
- Number of Revenue Entries: {len(st.session_state.revenue)}
- Average Revenue per Entry: ₹{st.session_state.revenue['Amount'].mean():,.0f}
- Highest Single Revenue: ₹{st.session_state.revenue['Amount'].max():,.0f}
- Most Profitable Source: {max(revenue_breakdown, key=revenue_breakdown.get) if revenue_breakdown else 'N/A'}

EXPENSE ANALYSIS:
- Total Expenses: ₹{total_expenses:,.0f}
- Expense Breakdown by Category: {expense_breakdown}
- Number of Expense Entries: {len(st.session_state.expenses)}
- Average Expense per Entry: ₹{st.session_state.expenses['Amount'].mean():,.0f}
- Highest Single Expense: ₹{st.session_state.expenses['Amount'].max():,.0f}
- Biggest Expense Category: {max(expense_breakdown, key=expense_breakdown.get) if expense_breakdown else 'N/A'}

PROFITABILITY:
- Net Profit: ₹{net_profit:,.0f}
- Profit Margin: {profit_margin:.1f}%
- Status: {'Profitable' if net_profit > 0 else 'Loss-making'}

Provide specific, actionable advice based on this real data. Use Indian Rupees (₹) for all amounts.
Be practical and consider that this is a cafe/restaurant business.
        """
        
        # Quick Questions
        st.markdown("### 📌 Quick Questions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Analyze Profit Margin", use_container_width=True):
                st.session_state.ai_question = f"My current profit margin is {profit_margin:.1f}%. Is this healthy for a cafe? How can I improve it?"
            
            if st.button("💸 Reduce Costs", use_container_width=True):
                st.session_state.ai_question = "What are the top 5 ways I can reduce costs at Feeka Cafe based on my expense breakdown?"
        
        with col2:
            if st.button("📈 Increase Revenue", use_container_width=True):
                st.session_state.ai_question = "Based on my revenue sources, which channel should I focus on to increase profits?"
            
            if st.button("🎯 Set Goals", use_container_width=True):
                st.session_state.ai_question = "Based on my current financial performance, what realistic monthly goals should I set for Feeka Cafe?"
        
        with col3:
            if st.button("⚠️ Risk Analysis", use_container_width=True):
                st.session_state.ai_question = "What financial risks do you see in my current data? How can I mitigate them?"
            
            if st.button("📋 Full Review", use_container_width=True):
                st.session_state.ai_question = "Give me a complete financial health review of Feeka Cafe with specific recommendations."
        
        # Question Input
        st.markdown("---")
        user_question = st.text_area(
            "💬 Ask your financial question:",
            value=st.session_state.get('ai_question', ''),
            placeholder="Example: How can I improve my profit margin?",
            height=100
        )
        
        if st.button("🤖 Get AI Advice", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("🤔 AI Advisor is analyzing your data..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": financial_context},
                                {"role": "user", "content": user_question}
                            ],
                            temperature=0.7,
                            max_tokens=1500
                        )
                        
                        advice = response.choices[0].message.content
                        
                        st.markdown("---")
                        st.markdown("### 💡 AI Advisor Response")
                        st.markdown(advice)
                        
                        # Save to history
                        st.session_state.advice_history.append({
                            'timestamp': current_time.strftime('%d %b %Y %I:%M %p'),
                            'question': user_question,
                            'advice': advice,
                            'financials': {
                                'revenue': total_revenue,
                                'expenses': total_expenses,
                                'profit': net_profit,
                                'margin': profit_margin
                            }
                        })
                        
                        # Clear the question
                        st.session_state.ai_question = ''
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure your API key is valid and has credits")
            else:
                st.warning("⚠️ Please enter a question")
        
        # Advice History
        if st.session_state.advice_history:
            st.markdown("---")
            st.markdown("### 📚 Consultation History")
            
            for i, item in enumerate(reversed(st.session_state.advice_history[-5:])):
                with st.expander(f"📝 {item['question'][:50]}... | {item['timestamp']}"):
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown(f"**Data Snapshot:** Revenue: ₹{item['financials']['revenue']:,.0f} | Expenses: ₹{item['financials']['expenses']:,.0f} | Profit: ₹{item['financials']['profit']:,.0f}")
                    st.markdown("---")
                    st.markdown(f"**Advice:**\n{item['advice']}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px; color: {text_color}; opacity: 0.7;">
    <p>🍽️ <strong>Feeka Cafe Budget Manager</strong></p>
    <p>Powered by OpenAI GPT-4 & Streamlit | 💾 Auto-save enabled</p>
    <p style="font-size: 0.8rem;">Theme: {st.session_state.theme.capitalize()} Mode | Last updated: {current_time.strftime('%d %b %Y %I:%M %p')}</p>
</div>
""", unsafe_allow_html=True)
