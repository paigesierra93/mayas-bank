import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- SETUP: FILE HANDLING ---
DATA_FILE = "ledger.csv"

def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Date", "Client", "Type", "Amount", "Note", "Savings_Balance", "Niece_Earnings"])
    return pd.read_csv(DATA_FILE)

def save_transaction(client_name, type, amount, note, savings_change, earnings_change):
    df = load_data()
    
    # Filter for this specific client to find THEIR current balance
    client_data = df[df["Client"] == client_name]
    
    if not client_data.empty:
        current_savings = client_data.iloc[-1]["Savings_Balance"]
    else:
        current_savings = 0.0

    new_savings = current_savings + savings_change

    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Client": client_name,
        "Type": type,
        "Amount": amount,
        "Note": note,
        "Savings_Balance": new_savings,
        "Niece_Earnings": earnings_change 
    }])

    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return new_savings

# --- PAGE CONFIG ---
st.set_page_config(page_title="Future Accountant Suite", page_icon="🎄")

# --- INITIALIZE SESSION STATE (For the Intro) ---
if 'intro_seen' not in st.session_state:
    st.session_state['intro_seen'] = False

# ==========================================
# PART 1: THE CHRISTMAS WELCOME SCREEN
# ==========================================
if not st.session_state['intro_seen']:
    st.snow() # ❄️ Let it snow!
    
    st.markdown("""
    <style>
    .christmas-card {
        background-color: #f0f2f6;
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #ff4b4b;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="christmas-card">', unsafe_allow_html=True)
    st.title("🎄 Merry Christmas, Maya! 🎄")
    st.write("### To my beautiful and smart niece,")
    st.write("""
    I've created this software for you so you can begin your journey into your future. 
    You have such a bright path ahead of you in accounting, and every accountant needs 
    their first set of books.
    
    I hope this tool will help you learn how money grows, how to track clients, 
    and how to build your own wealth.
    
    If you find any bugs in it or need a new feature, let me know (that's part of the job!).
    """)
    st.write("**Love,**")
    st.write("**Aunt Paige**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.header("⚡ Mini Tutorial: How to be the Boss")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("1. **Create Clients**\nUse the sidebar to add people (Like Me, Mom, or You).")
    with col2:
        st.info("2. **Process Money**\nEnter deposits. You must calculate your 15% cut correctly!")
    with col3:
        st.info("3. **Track Profits**\nWatch your 'Accountant Earnings' grow automatically.")

    st.write("")
    if st.button("🚀 Launch My Accounting System", type="primary"):
        st.session_state['intro_seen'] = True
        st.rerun()

# ==========================================
# PART 2: THE BANKING APP (Hidden until button click)
# ==========================================
else:
    df = load_data()

    # --- SIDEBAR: CLIENT MANAGEMENT ---
    st.sidebar.header("👥 Client Management")

    existing_clients = df["Client"].unique().tolist() if not df.empty else []
    menu_options = ["➕ Create New Client"] + existing_clients

    selected_option = st.sidebar.selectbox("Select Account", menu_options)

    if selected_option == "➕ Create New Client":
        new_client_name = st.sidebar.text_input("Enter New Client Name:")
        if st.sidebar.button("Create Account"):
            if new_client_name and new_client_name not in existing_clients:
                save_transaction(new_client_name, "Account Open", 0, "Account Created", 0, 0)
                st.sidebar.success(f"Account for {new_client_name} created!")
                st.rerun()
        st.title("Welcome to Family Trust Bank")
        st.info("👈 Please create or select a client in the sidebar to begin.")
        st.stop() 
    else:
        current_client = selected_option

    # --- CALCULATE TOTALS ---
    total_earnings = df["Niece_Earnings"].sum()

    client_df