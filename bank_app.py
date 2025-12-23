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
    # Initializes 3 empty goals if file doesn't exist
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
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Category": category, 
        "Item": item, "Amount": amount, "Sass_Level": sass
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(PERSONAL_FILE, index=False)

def update_goal(goal_name, amount_change):
    df = load_goals()
    # Update the specific goal's balance
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

# --- SASS ENGINE ---
def get_sass(mood):
    if mood == "good_math": return random.choice(["Period. 💅", "Math Wizard energy.", "Stonks 📈"])
    elif mood == "bad_math": return random.choice(["Bestie, the math ain't mathing.", "Bombastic Side Eye. 👀"])
    elif mood == "spending": return random.choice(["Capitalism wins again.", "RIP your wallet. 💀", "I hope it was on sale."])
    elif mood == "saving": return random.choice(["Secure the bag. 💰", "Rich Auntie Energy.", "Look at you, being responsible."])
    elif mood == "goal_hit": return random.choice(["WE DID IT JOE!", "Slayed the house down.", "Look at you winning life! 🏆"])
    elif mood == "early_withdraw": return random.choice(["Quitting halfway? Ouch.", "Are you sure? You were doing so well.", "Commitment issues?"])

# --- CONFIG & STYLE ---
st.set_page_config(page_title="Maya's Empire", page_icon="💅", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Courier New', sans-serif; }
    .quote-box { background-color: #262730; border-left: 5px solid #ff4b4b; padding: 20px; font-style: italic; color: #fff; margin-bottom: 20px;}
    .goal-card { background-color: #1c1e26; padding: 15px; border-radius: 10px; border: 1px solid #4b4b4b; text-align: center; }
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
        # ... (Other client actions kept same for brevity)
        elif action == "Charge Penalty":
            days = st.number_input("Days Late", min_value=1)
            penalty = days * 5.00
            if st.button("Charge Penalty 💀"):
                save_client_transaction(current_client, "Penalty", penalty, "Late Fee", 0, penalty)
                st.success("Penalty Charged.")
                st.rerun()

    with tab2:
        st.dataframe(client_df.sort_index(ascending=False), use_container_width=True)

# ==========================================
# ZONE 2: MY EMPIRE (BUDGET & GOALS)
# ==========================================
elif mode == "👛 My Empire (Budget)":
    quote = get_daily_quote()
    st.toast(f"✨ Daily Vibe: {quote}")
    st.title("👛 My Empire")
    st.markdown(f'<div class="quote-box">📅 <strong>Daily Wisdom:</strong> "{quote}"</div>', unsafe_allow_html=True)

    # --- 1. CALCULATE REAL CASH ---
    client_df = load_client_data()
    personal_df = load_personal_data()
    goals_df = load_goals()
    
    total_earned = client_df["Niece_Earnings"].sum() if not client_df.empty else 0.0
    total_spent = personal_df[personal_df["Category"] == "Spending"]["Amount"].sum() # Regular spending
    
    # Calculate total currently locked inside goals
    total_in_goals = goals_df["Balance"].sum()
    
    # Available Cash = (Total Earned - Total Spent) - (Money currently sitting in goals)
    available_cash = total_earned - total_spent - total_in_goals

    # --- 2. GOAL DASHBOARD ---
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

    # --- 3. MONEY MOVER ---
    st.markdown("---")
    st.subheader("💸 Money Mover")
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.caption("Move money between Cash and Goals")
        
        # SOURCE SELECTION
        source_options = ["Available Cash"] + goal_names
        source = st.selectbox("From (Source):", source_options)
        
        # DESTINATION SELECTION
        dest_options = ["Available Cash"] + goal_names + ["💸 SPENDING (Gone forever)"]
        # Remove source from destination options to avoid moving to self
        dest_options = [d for d in dest_options if d != source]
        destination = st.selectbox("To (Destination):", dest_options)
        
        amount = st.number_input("Amount ($)", min_value=0.01, value=10.00)
        
        # --- LOGIC & BUTTONS ---
        
        # CASE A: SAVING (Cash -> Goal)
        if source == "Available Cash" and destination in goal_names:
            if st.button("Stash it 💰"):
                if amount > available_cash:
                    st.error("You're broke bestie. Not enough cash.")
                else:
                    update_goal(destination, amount)
                    save_personal_transaction("Savings Transfer", f"Saved to {destination}", 0, get_sass("saving"))
                    st.balloons()
                    st.success(f"Saved ${amount} to {destination}!")
                    st.rerun()

        # CASE B: SPENDING (Cash -> Gone)
        elif source == "Available Cash" and destination == "💸 SPENDING (Gone forever)":
            item = st.text_input("What did you buy?")
            if st.button("Buy it 🛍️"):
                if amount > available_cash:
                    st.error("Insufficient funds.")
                else:
                    save_personal_transaction("Spending", item, amount, get_sass("spending"))
                    st.warning("Cash spent.")
                    st.rerun()

        # CASE C: WITHDRAWING (Goal -> Cash)
        elif source in goal_names and destination == "Available Cash":
            # Get current goal stats
            goal_row = goals_df[goals_df["Name"] == source].iloc[0]
            current_bal = goal_row["Balance"]
            target = goal_row["Target"]
            
            if amount > current_bal:
                st.error(f"You only have ${current_bal} in {source}.")
            else:
                # CHECK: IS GOAL MET?
                if current_bal >= target:
                    # HAPPY PATH
                    st.success("🎉 GOAL REACHED! You earned this.")
                    if st.button("Cash Out & Recycle Goal ♻️"):
                        update_goal(source, -amount) # Remove money
                        # Trigger Recycle Form
                        st.session_state['recycle_mode'] = source
                        st.experimental_rerun()
                else:
                    # WARNING PATH
                    st.warning(f"⚠️ Wait! You only have ${current_bal}/${target}. {get_sass('early_withdraw')}")
                    if st.button("I don't care, I need the money"):
                        update_goal(source, -amount)
                        save_personal_transaction("Early Withdrawal", f"Took from {source}", 0, "Quitter.")
                        st.error(f"Withdrew ${amount}. Goal progress lost.")
                        st.rerun()

        # CASE D: TRANSFER (Goal -> Goal)
        elif source in goal_names and destination in goal_names:
            source_bal = goals_df[goals_df["Name"] == source].iloc[0]["Balance"]
            if st.button("Transfer"):
                if amount > source_bal:
                    st.error("Not enough funds.")
                else:
                    update_goal(source, -amount)
                    update_goal(destination, amount)
                    st.success(f"Moved ${amount} from {source} to {destination}.")
                    st.rerun()

    # --- 4. GOAL SETTINGS / RECYCLE ---
    with c2:
        st.write("### ⚙️ Goal Settings")
        
        # Handle Recycle Mode (renaming a completed goal)
        if 'recycle_mode' in st.session_state:
            old_name = st.session_state['recycle_mode']
            st.info(f"♻️ Recycling '{old_name}'! Pick a new goal.")
            new_name_input = st.text_input("New Goal Name", value="New Goal")
            new_target_input = st.number_input("New Target Amount", value=500.0)
            
            if st.button("Set New Goal"):
                reset_goal(old_name, new_name_input, new_target_input)
                del st.session_state['recycle_mode']
                st.balloons()
                st.success("New Goal Set! Good luck!")
                st.rerun()
        
        # Standard Edit Mode
        else:
            with st.expander("Edit Goal Names & Targets"):
                edit_goal = st.selectbox("Edit which goal?", goal_names)
                new_n = st.text_input("Rename:", value=edit_goal)
                new_t = st.number_input("New Target:", value=1000.0)
                if st.button("Update Goal"):
                    # We reuse the reset function but keep the balance if needed, 
                    # but typically editing resets logic. Let's just update metadata manually.
                    # Simpler: Just update the CSV directly here for rename.
                    idx = goals_df.index[goals_df['Name'] == edit_goal].tolist()[0]
                    goals_df.at[idx, 'Name'] = new_n
                    goals_df.at[idx, 'Target'] = new_t
                    goals_df.to_csv(GOALS_FILE, index=False)
                    st.success("Updated!")
                    st.rerun()

        st.markdown("---")
        st.metric("💵 Cash Available to Spend/Save", f"${available_cash:,.2f}")