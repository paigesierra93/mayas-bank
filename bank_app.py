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
    selected_client = st.sidebar.selectbox("Select Client", client_menu)

    if selected_client == "➕ Add New Client":
        new_name = st.sidebar.text_input("Client Name")
        if st.sidebar.button("Add Client"):
            if new_name and new_name not in existing_clients:
                save_client_transaction(new_name, "Open", 0, "Welcome", 0, 0)
                st.rerun()
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
                    note = "Deposit (Auto-Fixed)"
                save_client_transaction(current_client, "Deposit", amount, note, client_save, real_earn)
                st.rerun()
        elif action == "Charge Penalty":
            days = st.number_input("Days Late", min_value=1)
            penalty = days * 5.00
            if st.button("Charge Penalty 💀"):
                save_client_transaction(current_client, "Penalty", penalty, "Late Fee", 0, penalty)
                st.success("Penalty Charged.")
                st.rerun()
        elif action == "Client Withdrawal":
            amount = st.number_input("Withdraw Amount", min_value=0.0)
            if st.button("Process"):
                 if amount <= client_balance:
                    save_client_transaction(current_client, "Withdrawal", amount, "Client access", -amount, 0)
                    st.success("Processed.")
                    st.rerun()

    with tab2:
        st.dataframe(client_df.sort_index(ascending=False), use_container_width=True)

# ==========================================
# ZONE 2: MY EMPIRE
# ==========================================
elif mode == "👛 My Empire (Budget)":
    quote = get_daily_quote()
    st.toast(f"✨ Daily Vibe: {quote}")
    st.title("👛 My Empire")
    st.markdown(f'<div class="quote-box">📅 <strong>Daily Wisdom:</strong> "{quote}"</div>', unsafe_allow_html=True)

    client_df = load_client_data()
    personal_df = load_personal_data()
    goals_df = load_goals()
    
    total_earned = client_df["Niece_Earnings"].sum() if not client_df.empty else 0.0
    total_spent = abs(personal_df[personal_df["Amount"] < 0]["Amount"].sum()) # Sum of all negatives
    total_refunds = personal_df[personal_df["Category"] == "Refund"]["Amount"].sum()
    
    # Net spent (Spending - Refunds)
    net_spent = total_spent - total_refunds
    
    total_in_goals = goals_df["Balance"].sum()
    available_cash = total_earned + personal_df["Amount"].sum() - total_in_goals

    # DASHBOARD
    st.subheader("🏆 The Goal Tracker")
    cols = st.columns(3)
    goal_names = goals_df["Name"].tolist()
    for index, row in goals_df.iterrows():
        with cols[index]:
            st.markdown(f"### {row['Name']}")
            progress = min(row['Balance'] / row['Target'], 1.0)
            st.progress(progress)
            st.write(f"**${row['Balance']:,.0f}** / ${row['Target']:,.0f}")
            if row['Balance'] >= row['Target']:
                st.success("GOAL MET! 🎉")

    st.markdown("---")
    st.subheader("💸 Money Mover")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.metric("💵 Cash Available", f"${available_cash:,.2f}")
        source_options = ["Available Cash"] + goal_names
        source = st.selectbox("From:", source_options)
        dest_options = ["Available Cash"] + goal_names + ["💸 SPENDING (Gone forever)"]
        dest_options = [d for d in dest_options if d != source]
        destination = st.selectbox("To:", dest_options)
        
        amount = st.number_input("Amount ($)", min_value=0.01, value=10.00)
        
        if st.button("Execute Transaction"):
            # A: SAVING
            if source == "Available Cash" and destination in goal_names:
                if amount > available_cash: st.error("Not enough cash.")
                else:
                    update_goal(destination, amount)
                    save_personal_transaction("Savings Transfer", f"Saved to {destination}", 0, get_sass("saving"))
                    st.balloons()
                    st.rerun()

            # B: SPENDING
            elif source == "Available Cash" and destination == "💸 SPENDING (Gone forever)":
                item = st.text_input("What did you buy?")
                if amount > available_cash: st.error("Insufficient funds.")
                else:
                    save_personal_transaction("Spending", item, amount, get_sass("spending"))
                    st.rerun()

            # C: WITHDRAWING
            elif source in goal_names and destination == "Available Cash":
                goal_row = goals_df[goals_df["Name"] == source].iloc[0]
                if amount > goal_row["Balance"]: st.error(f"Not enough in {source}.")
                else:
                    if goal_row["Balance"] >= goal_row["Target"]:
                        # GOAL MET WITHDRAWAL
                        update_goal(source, -amount)
                        save_personal_transaction("Reward", f"Cashed out {source}", amount, get_sass("goal_hit"))
                        st.session_state['recycle_mode'] = source
                        st.experimental_rerun()
                    else:
                        # EARLY WITHDRAWAL
                        update_goal(source, -amount)
                        save_personal_transaction("Early Withdrawal", f"Took from {source}", 0, get_sass("early_withdraw"))
                        st.rerun()

            # D: TRANSFER
            elif source in goal_names and destination in goal_names:
                src_bal = goals_df[goals_df["Name"] == source].iloc[0]["Balance"]
                if amount > src_bal: st.error("Not enough funds.")
                else:
                    update_goal(source, -amount)
                    update_goal(destination, amount)
                    st.success("Transferred.")
                    st.rerun()

        # RECYCLE LOGIC
        if 'recycle_mode' in st.session_state:
            old_name = st.session_state['recycle_mode']
            st.info(f"♻️ Recycling '{old_name}'!")
            new_n = st.text_input("New Name", value="New Goal")
            new_t = st.number_input("New Target", value=500.0)
            if st.button("Set New Goal"):
                reset_goal(old_name, new_n, new_t)
                del st.session_state['recycle_mode']
                st.rerun()

    with c2:
        st.write("### 📜 Transaction Feed")
        if not personal_df.empty:
            # Custom Feed Display
            for index, row in personal_df.sort_index(ascending=False).iterrows():
                # Determine Color
                amt = row['Amount']
                cat = row['Category']
                css_class = "pos" # Default green
                
                display_amt = f"+${abs(amt):.2f}"
                if amt < 0:
                    css_class = "neg"
                    display_amt = f"-${abs(amt):.2f}"
                if cat == "Reward":
                    css_class = "gold"
                    display_amt = f"+${abs(amt):.2f} (Reward)"

                # The Card HTML
                st.markdown(f"""
                <div class="history-card {css_class}">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>{row['Item']} ({row['Category']})</strong>
                        <span>{row['Date']}</span>
                    </div>
                    <div style="font-size: 20px; font-weight: bold;">{display_amt}</div>
                    <div style="font-style: italic; color: #bbb;">"{row['Sass_Level']}"</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No history yet.")