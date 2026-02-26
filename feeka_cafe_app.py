import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Feeka Cafe Budget Manager",
    page_icon="🍽️",
    layout="wide"
)

# ==================== THEME MANAGEMENT ====================
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Theme Colors
if st.session_state.theme == 'dark':
    bg_color = "#0E1117"
    text_color = "#FAFAFA"
    card_bg = "#262730"
else:
    bg_color = "#FFFFFF"
    text_color = "#262730"
    card_bg = "#F0F2F6"

# ==================== CUSTOM CSS ====================
st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .datetime-display {{
        position: fixed;
        top: 60px;
        right: 20px;
        font-size: 0.7rem;
        color: {text_color};
        opacity: 0.6;
        text-align: right;
        z-index: 999;
        background: {card_bg};
        padding: 8px 12px;
        border-radius: 8px;
    }}
    .main-title {{
        text-align: center;
        color: #FF6B6B;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==================== DATE TIME ====================
now = datetime.now()
date_str = now.strftime("%A, %d %B %Y")
time_str = now.strftime("%I:%M:%S %p").lower()

st.markdown(f"""
<div class="datetime-display">
    {date_str}<br>{time_str}
</div>
""", unsafe_allow_html=True)

# ==================== DATA FUNCTIONS ====================
def get_default_revenue():
    return pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'Source': ['Dine-in', 'Takeaway', 'Delivery', 'Dine-in', 'Takeaway',
                   'Dine-in', 'Delivery', 'Dine-in', 'Takeaway', 'Dine-in'],
        'Description': ['Lunch', 'Coffee', 'Food', 'Dinner', 'Snacks',
                       'Brunch', 'Orders', 'Service', 'Morning', 'Evening'],
        'Amount': [4500, 2200, 1800, 5200, 1500, 6800, 2100, 4800, 1900, 5500]
    })

def get_default_expenses():
    return pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'Category': ['Ingredients', 'Rent', 'Salaries', 'Utilities', 'Ingredients',
                     'Marketing', 'Maintenance', 'Ingredients', 'Supplies', 'Utilities'],
        'Description': ['Vegetables', 'Monthly rent', 'Staff pay', 'Electricity',
                       'Coffee beans', 'Ads', 'Repair', 'Meat', 'Cleaning', 'Water'],
        'Amount': [2500, 15000, 25000, 3500, 4000, 2000, 1500, 3500, 800, 1200]
    })

# Initialize data
if 'revenue' not in st.session_state:
    st.session_state.revenue = get_default_revenue()

if 'expenses' not in st.session_state:
    st.session_state.expenses = get_default_expenses()

if 'advice_history' not in st.session_state:
    st.session_state.advice_history = []

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🍽️ Feeka Cafe")
    st.markdown("---")
    
    # Theme Toggle
    st.markdown("### 🎨 Theme")
    theme_btn = "🌙 Dark Mode" if st.session_state.theme == 'light' else "☀️ Light Mode"
    if st.button(theme_btn, use_container_width=True):
        toggle_theme()
        st.rerun()
    
    st.markdown("---")
    
    # API Key
    st.markdown("### 🔑 API Key")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    
    st.markdown("---")
    
    # Export/Import
    st.markdown("### 💾 Data")
    
    # Export Revenue
    rev_json = st.session_state.revenue.to_json(orient='records', date_format='iso')
    st.download_button(
        "📊 Export Revenue",
        rev_json,
        f"revenue_{now.strftime('%Y%m%d')}.json",
        use_container_width=True
    )
    
    # Export Expenses
    exp_json = st.session_state.expenses.to_json(orient='records', date_format='iso')
    st.download_button(
        "💸 Export Expenses",
        exp_json,
        f"expenses_{now.strftime('%Y%m%d')}.json",
        use_container_width=True
    )
    
    # Import
    uploaded_rev = st.file_uploader("Import Revenue", type=['json'], key='rev')
    if uploaded_rev:
        try:
            df = pd.read_json(uploaded_rev)
            df['Date'] = pd.to_datetime(df['Date'])
            st.session_state.revenue = df
            st.success("✅ Imported!")
            st.rerun()
        except:
            st.error("❌ Invalid file")
    
    uploaded_exp = st.file_uploader("Import Expenses", type=['json'], key='exp')
    if uploaded_exp:
        try:
            df = pd.read_json(uploaded_exp)
            df['Date'] = pd.to_datetime(df['Date'])
            st.session_state.expenses = df
            st.success("✅ Imported!")
            st.rerun()
        except:
            st.error("❌ Invalid file")
    
    st.markdown("---")
    st.markdown("[Get API Key](https://platform.openai.com/api-keys)")

# ==================== MAIN CONTENT ====================
st.markdown('<h1 class="main-title">🍽️ Feeka Cafe Budget Manager</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; opacity: 0.7;">Complete Financial Management System</p>', unsafe_allow_html=True)

# Calculate totals
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
    st.subheader("💰 Financial Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    with col2:
        st.metric("Total Expenses", f"₹{total_expenses:,.0f}")
    with col3:
        st.metric("Net Profit", f"₹{net_profit:,.0f}")
    with col4:
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Revenue vs Expenses")
        fig = go.Figure(data=[
            go.Bar(name='Revenue', x=['Total'], y=[total_revenue]),
            go.Bar(name='Expenses', x=['Total'], y=[total_expenses])
        ])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Expense Breakdown")
        exp_cat = st.session_state.expenses.groupby('Category')['Amount'].sum()
        fig = px.pie(values=exp_cat.values, names=exp_cat.index)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: REVENUE ====================
with tab2:
    st.subheader("📈 Revenue Management")
    
    with st.expander("➕ Add Revenue"):
        with st.form("add_revenue", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                date = st.date_input("Date", datetime.now())
            with col2:
                source = st.selectbox("Source", ["Dine-in", "Takeaway", "Delivery", "Catering"])
            with col3:
                desc = st.text_input("Description")
            with col4:
                amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("Add", use_container_width=True):
                if amount > 0 and desc:
                    new_row = pd.DataFrame({
                        'Date': [pd.Timestamp(date)],
                        'Source': [source],
                        'Description': [desc],
                        'Amount': [amount]
                    })
                    st.session_state.revenue = pd.concat([st.session_state.revenue, new_row], ignore_index=True)
                    st.success(f"✅ Added ₹{amount:,.0f}")
                    st.rerun()
    
    st.markdown("---")
    
    # Revenue table
    st.subheader("📋 All Entries")
    display_df = st.session_state.revenue.sort_values('Date', ascending=False).copy()
    display_df['Delete'] = False
    
    edited = st.data_editor(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Delete": st.column_config.CheckboxColumn("Delete?"),
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Amount": st.column_config.NumberColumn("Amount", format="₹%.0f")
        }
    )
    
    if st.button("🗑️ Delete Selected"):
        keep = edited[edited['Delete'] == False].drop('Delete', axis=1)
        if len(keep) < len(st.session_state.revenue):
            st.session_state.revenue = keep.reset_index(drop=True)
            st.success("✅ Deleted!")
            st.rerun()
    
    # Chart
    st.markdown("---")
    st.subheader("📊 Revenue by Source")
    rev_source = st.session_state.revenue.groupby('Source')['Amount'].sum()
    fig = px.bar(rev_source)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 3: EXPENSES ====================
with tab3:
    st.subheader("💸 Expense Management")
    
    with st.expander("➕ Add Expense"):
        with st.form("add_expense", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.now())
                category = st.selectbox("Category", 
                    ["Ingredients", "Rent", "Salaries", "Utilities", "Marketing", 
                     "Maintenance", "Supplies", "Other"])
            
            with col2:
                desc = st.text_input("Description")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            
            if st.form_submit_button("Add", use_container_width=True):
                if amount > 0 and desc:
                    new_row = pd.DataFrame({
                        'Date': [pd.Timestamp(date)],
                        'Category': [category],
                        'Description': [desc],
                        'Amount': [amount]
                    })
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_row], ignore_index=True)
                    st.success(f"✅ Added ₹{amount:,.0f}")
                    st.rerun()
    
    st.markdown("---")
    
    # Expense table
    st.subheader("📋 All Entries")
    display_df = st.session_state.expenses.sort_values('Date', ascending=False).copy()
    display_df['Delete'] = False
    
    edited = st.data_editor(
        display_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Delete": st.column_config.CheckboxColumn("Delete?"),
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Amount": st.column_config.NumberColumn("Amount", format="₹%.0f")
        }
    )
    
    if st.button("🗑️ Delete Selected", key="del_exp"):
        keep = edited[edited['Delete'] == False].drop('Delete', axis=1)
        if len(keep) < len(st.session_state.expenses):
            st.session_state.expenses = keep.reset_index(drop=True)
            st.success("✅ Deleted!")
            st.rerun()
    
    # Chart
    st.markdown("---")
    st.subheader("📊 Expenses by Category")
    exp_cat = st.session_state.expenses.groupby('Category')['Amount'].sum()
    fig = px.bar(exp_cat)
    st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 4: REPORTS ====================
with tab4:
    st.subheader("📊 Financial Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Revenue Summary")
        rev_sum = st.session_state.revenue.groupby('Source')['Amount'].sum()
        for source, amt in rev_sum.items():
            st.write(f"**{source}:** ₹{amt:,.0f}")
        st.write(f"**Total:** ₹{total_revenue:,.0f}")
    
    with col2:
        st.markdown("### Expense Summary")
        exp_sum = st.session_state.expenses.groupby('Category')['Amount'].sum()
        for cat, amt in exp_sum.items():
            st.write(f"**{cat}:** ₹{amt:,.0f}")
        st.write(f"**Total:** ₹{total_expenses:,.0f}")
    
    st.markdown("---")
    st.markdown(f"### Net Profit: ₹{net_profit:,.0f}")
    st.markdown(f"### Profit Margin: {profit_margin:.1f}%")
    
    st.markdown("---")
    
    # Download reports
    col1, col2 = st.columns(2)
    
    with col1:
        rev_csv = st.session_state.revenue.to_csv(index=False)
        st.download_button("📊 Download Revenue CSV", rev_csv, "revenue.csv")
    
    with col2:
        exp_csv = st.session_state.expenses.to_csv(index=False)
        st.download_button("💸 Download Expenses CSV", exp_csv, "expenses.csv")

# ==================== TAB 5: AI ADVISOR ====================
with tab5:
    st.subheader("🤖 AI Finance Advisor")
    
    if not api_key:
        st.warning("⚠️ Enter OpenAI API Key in sidebar")
        st.info("Get key at: https://platform.openai.com/api-keys")
    else:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            context = f"""
You are a financial advisor for Feeka Cafe.

Current Data:
- Total Revenue: ₹{total_revenue:,.0f}
- Total Expenses: ₹{total_expenses:,.0f}
- Net Profit: ₹{net_profit:,.0f}
- Profit Margin: {profit_margin:.1f}%

Revenue by Source: {st.session_state.revenue.groupby('Source')['Amount'].sum().to_dict()}
Expenses by Category: {st.session_state.expenses.groupby('Category')['Amount'].sum().to_dict()}

Provide specific advice for this cafe business.
"""
            
            # Quick buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Analyze Profit"):
                    st.session_state.ai_q = f"My profit margin is {profit_margin:.1f}%. How can I improve?"
            
            with col2:
                if st.button("💸 Reduce Costs"):
                    st.session_state.ai_q = "What are top ways to reduce costs?"
            
            with col3:
                if st.button("📈 Increase Revenue"):
                    st.session_state.ai_q = "How can I increase revenue?"
            
            # Question input
            question = st.text_area(
                "Ask a question:",
                value=st.session_state.get('ai_q', ''),
                placeholder="e.g., How can I improve my profit margin?"
            )
            
            if st.button("🤖 Get Advice", type="primary"):
                if question:
                    with st.spinner("Analyzing..."):
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": context},
                                    {"role": "user", "content": question}
                                ]
                            )
                            
                            advice = response.choices[0].message.content
                            
                            st.markdown("---")
                            st.markdown("### 💡 Advice:")
                            st.markdown(advice)
                            
                            st.session_state.advice_history.append({
                                'time': now.strftime('%d %b %I:%M %p'),
                                'question': question,
                                'advice': advice
                            })
                            
                            st.session_state.ai_q = ''
                            
  except 
