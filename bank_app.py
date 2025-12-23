import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# --- SETUP: FILE HANDLING ---
CLIENT_FILE = "ledger.csv"
PERSONAL_FILE = "my_budget.csv"
QUOTES_FILE = "quotes.csv"  # <--- Make sure your file is named this!

# --- DATA LOADING FUNCTIONS ---
def load_client_data():
    if not os.path.exists(CLIENT_FILE):
        return pd.DataFrame(columns=["Date", "Client", "Type", "Amount", "Note", "Savings_Balance", "Niece_Earnings"])
    return pd.read_csv(CLIENT_FILE)

def load_personal_data():
    if not os.path.exists(PERSONAL_FILE):
        return pd.DataFrame(columns=["Date", "Category", "Item", "Amount", "Sass_Level"])
    return pd.read_csv(PERSONAL_FILE)

def get_daily_quote():
    # 1. Check if file exists
    if not os.path.exists(QUOTES_FILE):
        return "Money looks better in the bank than on your feet." # Backup if file is missing
    
    try:
        # 2. Load the quotes
        df = pd.read_csv(QUOTES_FILE)
        
        # 3. Get today's day number (1 to 365)
        day_of_year = datetime.now().timetuple().tm_yday
        
        # 4. Math to loop through your list
        # This ensures if you have 100 quotes or 365, it never crashes
        quote_index = (day_of_year - 1) % len(df)
        
        # 5. Get the text from YOUR specific column name
        return df.iloc[quote_index]['DailyMotoQuote']
    except Exception as e:
        return f"Secure the bag. (Error reading quotes: {e})"

# --- SAVE FUNCTIONS ---
def save_client_transaction(client_name, type, amount, note, savings_change, earnings_change):
    df = load_client_data()
    client_data = df[df["Client"] == client_name]
    current_savings = client_data.iloc[-1]["Savings_Balance"] if not client_data.empty else 0.0
    new_savings = current_savings + savings_change
    
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Client": client_name, "Type": type, "Amount": amount, "Note": note,
        "Savings_Balance": new_savings, "Niece_Earnings": earnings_change 
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CLIENT_FILE, index=False)

def save_personal_transaction(category, item, amount, sass):
    df = load_personal_data()
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Category": category, "Item": item, "Amount": amount, "Sass_Level": sass
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(PERSONAL_FILE, index=False)

# --- THE SASS ENGINE ---
def get_sass(mood):
    if mood == "good_math":
        return random.choice(["Period. 💅", "Math Wizard energy.", "We love an educated queen.", "Stonks 📈"])
    elif mood == "bad_math":
        return random.choice(["Bestie, the math ain't mathing.", "Girl, use a calculator...", "Bombastic Side Eye. 👀"])
    elif mood == "spending":
        return random.choice(["Capitalism wins again.", "RIP your wallet. 💀", "Buying happiness?", "I hope it was on sale."])
    elif mood == "saving":
        return random.choice(["Secure the bag. 💰", "Rich Auntie Energy.", "Look at you, being responsible."])

# --- PAGE CONFIG ---
st.set_page_config(page_title="Maya's Empire", page_icon="💅", layout="wide")

# --- STYLE ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Courier New', sans-serif; }
    .quote-box {
        background-color: #262730;
        border-left: 5px solid #ff4b4b;
        padding: 20px;
        border-radius: 5px;
        font-style: italic;
        font-size: 18px;
        margin-bottom: 20px;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# --- APP NAVIGATION ---
st.sidebar.title("💅 Navigation")
mode = st.sidebar.radio("Go to:", ["💼 The Firm (Clients)", "👛 My Empire (Budget)"])

# ==========================================
# ZONE 1: THE FIRM
# ==========================================
if mode == "💼 The Firm (Clients)":
    st.title("💼 The Firm: Client Management")
    st.caption("Manage other people's money. Collect your fees.")
    
    df = load_client_data()
    
    existing_clients = df["Client"].unique().tolist() if not df.empty else []
    client_menu = ["➕ Add New Client"] + existing_clients
    selected_client = st.sidebar.selectbox("Select Client", client_menu)

    if selected_client == "➕ Add New Client":
        new_name = st.sidebar.text_input("Client Name")
        if st.sidebar.button("Add Client"):
            if new_name and new_name not in existing_clients:
                save_client_transaction(new_name, "Open", 0, "Welcome", 0, 0)
                st.rerun()
        st.info("👈 Add a client to start.")
        st.stop()
    
    current_client = selected_client
    
    client_df = df[df["Client"] == current_client]
    client_balance = client_df.iloc[-1]["Savings_Balance"] if not client_df.empty else 0.0
    total_revenue = df["Niece_Earnings"].sum()

    st.sidebar.markdown("---")
    st.sidebar.metric("Your Total Earnings", f"${total_revenue:,.2f}")
    st.sidebar.metric(f"{current_client}'s Balance", f"${client_balance:,.2f}")

    tab1, tab2 = st.tabs(["💸 Transactions", "🧾 Ledger"])
    
    with tab1:
        st.subheader(f"Managing: {current_client}")
        action = st.radio("Action:", ["Incoming Deposit", "Client Withdrawal", "Charge Penalty"], horizontal=True)
        
        if action == "Incoming Deposit":
            amount = st.number_input("Deposit Amount", value=10.00)
            st.write(f"**Quiz:** What is 15% of ${amount}?")
            guess = st.number_input("Your Math:", value=0.00)
            
            if st.button("Secure the Bag 💰"):
                real_earn = round(amount * 0.15, 2)
                client_save = amount - real_earn
                if abs(guess - real_earn) < 0.01:
                    st.success(f"Correct! {get_sass('good_math')}")
                    st.balloons()
                    note = "Deposit (Math Correct)"
                else:
                    st.error(f"Wrong. Answer is ${real_earn}. {get_sass('bad_math')}")
                    note = "Deposit (Math Auto-Fixed)"
                save_client_transaction(current_client, "Deposit", amount, note, client_save, real_earn)
                st.rerun()

        elif action == "Client Withdrawal":
            amount = st.number_input("Withdraw Amount", min_value=0.0)
            if st.button("Process Withdrawal"):
                if amount <= client_balance:
                    save_client_transaction(current_client, "Withdrawal", amount, "Client access", -amount, 0)
                    st.success("Withdrawal processed.")
                    st.rerun()
                else:
                    st.error("Insufficient funds!")

        elif action == "Charge Penalty":
            days = st.number_input("Days Late", min_value=1)
            penalty = days * 5.00
            st.write(f"Penalty: ${penalty:.2f}")
            if st.button("Charge Penalty 💀"):
                save_client_transaction(current_client, "Penalty", penalty, "Late Fee", 0, penalty)
                st.success(f"Charged ${penalty} penalty.")
                st.rerun()
    with tab2:
        st.dataframe(client_df.sort_index(ascending=False), use_container_width=True)

# ==========================================
# ZONE 2: MY EMPIRE (BUDGET)
# ==========================================
elif mode == "👛 My Empire (Budget)":
    
    # --- DAILY QUOTE POP-UP ---
    quote = get_daily_quote()
    # 1. The Toast (Slides in bottom right)
    st.toast(f"✨ Daily Vibe: {quote}")
    
    # 2. The Banner (Shows at top of page)
    st.title("👛 My Empire: Personal Budget")
    st.markdown(f'<div class="quote-box">📅 <strong>Daily Wisdom:</strong> "{quote}"</div>', unsafe_allow_html=True)

    # --- CALCULATE MONEY ---
    client_df = load_client_data()
    personal_df = load_personal_data()
    total_income = client_df["Niece_Earnings"].sum() if not client_df.empty else 0.0
    total_spent = personal_df[personal_df["Category"] == "Spending"]["Amount"].sum()
    total_saved = personal_df[personal_df["Category"] == "Savings Goal"]["Amount"].sum()
    available_cash = total_income - (total_spent + total_saved)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income (The Firm)", f"${total_income:,.2f}")
    col2.metric("Available Cash", f"${available_cash:,.2f}", delta_color="normal")
    col3.metric("Total Saved", f"${total_saved:,.2f}", delta_color="inverse")
    
    st.markdown("---")
    st.subheader("Move Your Money")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        move_type = st.radio("What are we doing?", ["Saving (Good Girl)", "Spending (Bad Girl)"])
        amount = st.number_input("Amount", min_value=0.01, value=5.00)
        item_name = st.text_input("Description (e.g. 'Car Fund' or 'Iced Coffee')")
        
        if st.button("Execute Transaction"):
            if amount > available_cash:
                st.error(f"Bestie, you're broke. You only have ${available_cash:.2f}.")
            else:
                if "Spending" in move_type:
                    sass = get_sass("spending")
                    category = "Spending"
                    st.warning(sass)
                else:
                    sass = get_sass("saving")
                    category = "Savings Goal"
                    st.balloons()
                    st.success(sass)
                save_personal_transaction(category, item_name, amount, sass)
                st.rerun()

    with c2:
        st.write("### Your History")
        if not personal_df.empty:
            st.dataframe(personal_df.sort_index(ascending=False), height=300)
        else:
            st.info("No personal transactions yet.")