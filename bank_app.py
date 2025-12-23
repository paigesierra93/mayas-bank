import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# --- SETUP: FILE HANDLING ---
CLIENT_FILE = "ledger.csv"
PERSONAL_FILE = "my_budget.csv"
QUOTES_FILE = "quotes.csv"
GOALS_FILE = "goals.csv"

# --- DATA LOADING ---
def load_client_data():
    if not os.path.exists(CLIENT_FILE):
        return pd.DataFrame(columns=["Date", "Client", "Type", "Amount", "Note", "Savings_Balance", "Niece_Earnings"])
    return pd.read_csv(CLIENT_FILE)

def load_personal_data():
    if not os.path.exists(PERSONAL_FILE):
        return pd.DataFrame(columns=["Date", "Category", "Item", "Amount", "Sass_Level"])
    return pd.read_csv(PERSONAL_FILE)

def load_goals():
    if not os.path.exists(GOALS_FILE):
        data = {
            "Goal_ID": ["Goal 1", "Goal 2", "Goal 3"],
            "Name": ["Car", "College", "Concert"],
            "Target": [1000.0, 5000.0, 300.0],
            "Balance": [0.0, 0.0, 0.0]
        }
        df = pd.DataFrame(data)
        df.to_csv(GOALS_FILE, index=False)
        return df
    return pd.read_csv(GOALS_FILE)

def get_daily_quote():
    if not os.path.exists(QUOTES_FILE):
        return "Money looks better in the bank than on your feet."
    try:
        df = pd.read_csv(QUOTES_FILE)
        day_of_year = datetime.now().timetuple().tm_yday
        quote_index = (day_of_year - 1) % len(df)
        return df.iloc[quote_index]['DailyMotoQuote']
    except Exception as e:
        return f"Secure the bag. (Error: {e})"

# --- SAVE FUNCTIONS ---
def save_client_transaction(client_name, type, amount, note, savings_change, earnings_change):
    df = load_client_data()
    client_data = df[df["Client"] == client_name]
    current_savings = client_data.iloc[-1]["Savings_Balance"] if not client_data.empty else 0.0
    new_savings = current_savings + savings_change
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Client": client_name, "Type": type, 
        "Amount": amount, "Note": note, "Savings_Balance": new_savings, "Niece_Earnings": earnings_change 
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CLIENT_FILE, index=False)

def save_personal_transaction(category, item, amount, sass):
    df = load_personal_data()
    # If Spending or Withdrawal, make negative
    if category in ["Spending", "Withdraw from Savings", "Early Withdrawal"]:
        amount = -amount
    # If Refund (Spending -> Cash), it's positive, so we leave it positive.
    
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Category": category, 
        "Item": item, "Amount": amount, "Sass_Level": sass
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(PERSONAL_FILE, index=False)

def update_goal(goal_name, amount_change):
    df = load_goals()
    idx = df.index[df['Name'] == goal_name].tolist()[0]
    df.at[idx, 'Balance'] += amount_change
    df.to_csv(GOALS_FILE, index=False)

def reset_goal(goal_name, new_name, new_target):
    df = load_goals()
    idx = df.index[df['Name'] == goal_name].tolist()[0]
    df.at[idx, 'Name'] = new_name
    df.at[idx, 'Target'] = new_target
    df.at[idx, 'Balance'] = 0.0
    df.to_csv(GOALS_FILE, index=False)

# --- SASS ENGINE (Updated with your phrases) ---
def get_sass(mood):
    if mood == "good_math": return random.choice(["Period. 💅", "Math Wizard energy.", "Stonks 📈"])
    elif mood == "bad_math": return random.choice(["Bestie, the math ain't mathing.", "Bombastic Side Eye. 👀"])
    
    # NEW SPECIFIC PHRASES
    elif mood == "spending": 
        return random.choice([
            "There you go spending money money. 💸", 
            "Capitalism wins again.", 
            "RIP your wallet. 💀", 
            "I hope it was on sale."
        ])
    elif mood == "saving": 
        return random.choice([
            "Damn girl, look at you save! 💅", 
            "Secure the bag. 💰", 
            "Rich Auntie Energy.", 
            "Look at you, being responsible."
        ])
    elif mood == "goal_hit": 
        return "You earned it. Feels good huh? 🏆"
    
    elif mood == "early_withdraw": return "Quitting halfway? Ouch."
    elif mood == "refund": return "We love a return policy."

# --- CONFIG & STYLE ---
st.set_page_config(page_title="Maya's Empire", page_icon="💅", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Courier New', sans-serif; }
    .quote-box { background-color: #262730; border-left: 5px solid #ff4b4b; padding: 20px; font-style: italic; color: #fff; margin-bottom: 20px;}
    
    /* Transaction History Styles */
    .history-card { background-color: #1c1e26; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #555; }
    .pos { border-left-color: #00cc00; } /* Green for Saving */
    .neg { border-left-color: #ff4444; } /* Red for Spending */
    .gold { border-left-color: #ffd700; } /* Gold for Goal Hit */
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
st.sidebar.title("💅 Navigation")
mode = st.sidebar.radio("Go to:", ["💼 The Firm (Clients)", "👛 My Empire (Budget)"])

# ==========================================
# ZONE 1: THE FIRM
# ==========================================
if mode == "💼 The Firm (Clients)":
    st.title("💼 The Firm: Client Management")
    df = load_client_data()
    existing_clients = df["Client"].unique().tolist() if not df.empty else []
    client_menu = ["➕ Add New Client"] + existing_clients