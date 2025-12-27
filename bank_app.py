import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# --- FILE & FOLDER SETUP ---
CLIENT_FILE = "ledger.csv"
PERSONAL_FILE = "my_budget.csv"
QUOTES_FILE = "quotes.csv"
GOALS_FILE = "goals.csv"
FACTS_FILE = "facts.csv"
PIG_FILE = "pig_map.csv"

# --- BANNER FILES ---
EMPIRE_BANNER = "banner.png"
FIRM_BANNER = "firm_banner.png"

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

def get_daily_content(file_path, column_name, fallback):
    if not os.path.exists(file_path):
        return fallback
    try:
        df = pd.read_csv(file_path)
        day_of_year = datetime.now().timetuple().tm_yday
        index = (day_of_year - 1) % len(df)
        return df.iloc[index][column_name]
    except:
        return fallback

# --- HELPER: SMART BANNER ---
def show_smart_banner(base_name, fallback_title):
    possible_files = [f"{base_name}.png", f"{base_name}.PNG", f"{base_name}.jpg", f"{base_name}.JPG"]
    found = False
    for f in possible_files:
        if os.path.exists(f):
            st.image(f, use_column_width=True)
            found = True
            break
    if not found:
        st.title(fallback_title)

# --- PIGGY BANK LOGIC ---
def get_pig_image(current_percent):
    if not os.path.exists(PIG_FILE):
        return None
    try:
        df = pd.read_csv(PIG_FILE)
        df = df.sort_values(by="Threshold")
        selected_image = df.iloc[0]["Image_File"]
        for index, row in df.iterrows():
            if current_percent >= row["Threshold"]:
                selected_image = row["Image_File"]
        return selected_image
    except:
        return None

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
    if category in ["Spending", "Withdraw from Savings", "Early Withdrawal"]:
        amount = -amount
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

# --- SASS ENGINE ---
def get_sass(mood):
    if mood == "good_math": return random.choice(["Period. 💅", "Math Wizard energy.", "Stonks 📈"])
    elif mood == "bad_math": return random.choice(["Bestie, the math ain't mathing.", "Bombastic Side Eye. 👀"])
    elif mood == "spending": return random.choice(["There you go spending money money. 💸", "Capitalism wins again.", "RIP your wallet. 💀"])
    elif mood == "saving": return random.choice(["Damn girl, look at you save! 💅", "Secure the bag. 💰", "Rich Auntie Energy."])
    elif mood == "goal_hit": return "You earned it. Feels good huh? 🏆"
    elif mood == "early_withdraw": return "Quitting halfway? Ouch."
    elif mood == "refund": return "We love a return policy."
    elif mood == "gift": return random.choice(["We love a rich relative. 💅", "Girl math: It's free money.", "Grandma came through! 👵💸"])

# --- CONFIG & STYLE ---
st.set_page_config(page_title="Maya's Empire", page_icon="💅", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Courier New', sans-serif; }
    .quote-box { background-color: #262730; border-left: 5px solid #ff4b4b; padding: 20px; font-style: italic; color: #fff; margin-bottom: 20px;}
    .history-card { background-color: #1c1e26; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #555; }
    .pos { border-left-color: #00cc00; }
    .neg { border-left-color: #ff4444; }
    .gold { border-left-color: #ffd700; }
    
    /* CUSTOM TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- INTRO LOGIC ---
if 'intro_seen' not in st.session_state:
    st.session_state['intro_seen'] = False

if not st.session_state['intro_seen']:
    is_first_run = not os.path.exists(CLIENT_FILE)
    if is_first_run:
        st.snow()
        st.title("🎄 Merry Christmas, Maya! 🎄")
        st.write("Welcome to your Empire. Let's make some money.")
        if st.button("🚀 Launch System"):
            st.session_state['intro_seen'] = True
            st.rerun()
    else:
        daily_fact = get_daily_content(FACTS_FILE, "Fun Fact", "Accountants are the rock stars of business.")
        st.markdown(f"### 🧠 Fact: {daily_fact}")
        if st.button("✨ Enter Empire Mode ✨"):
            st.session_state['intro_seen'] = True
            st.rerun()

# --- MAIN NAVIGATION (TOP TABS) ---
else:
    # 1. TOP LEVEL NAVIGATION
    tab_firm, tab_empire, tab_help = st.tabs(["💼 The Firm", "👛 My Empire", "❓ Boss Manual"])

    # ==========================
    # TAB 1: THE FIRM
    # ==========================
    with tab_firm:
        show_smart_banner("firm_banner", "💼 The Firm")
        
        # 2. SUB-NAVIGATION (The Firm)
        firm_sub_nav = st.radio("Menu:", ["📊 Dashboard", "📝 Add Client", "💸 Transaction"], horizontal=True, label_visibility="collapsed")
        st.markdown("---")

        df = load_client_data()
        existing_clients = df["Client"].unique().tolist() if not df.empty else []
        
        # A. DASHBOARD VIEW
        if firm_sub_nav == "📊 Dashboard":
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_client = st.selectbox("Select Client", existing_clients) if existing_clients else None
            
            if selected_client:
                client_df = df[df["Client"] == selected_client]
                bal = client_df.iloc[-1]["Savings_Balance"] if not client_df.empty else 0.0
                revenue = df["Niece_Earnings"].sum()
                
                col_a, col_b = st.columns(2)
                col_a.metric(f"{selected_client}'s Balance", f"${bal:,.2f}")
                col_b.metric("Your Total Earnings", f"${revenue:,.2f}")
                
                st.dataframe(client_df[["Date", "Type", "Amount", "Note", "Savings_Balance"]].sort_index(ascending=False), use_container_width=True)
            else:
                st.info("No clients yet. Go to 'Add Client'!")

        # B. ADD CLIENT VIEW
        elif firm_sub_nav == "📝 Add Client":
            st.subheader("New Client Onboarding")
            new_name = st.text_input("Client Name")
            if st.button("Create Account"):
                if new_name and new_name not in existing_clients:
                    save_client_transaction(new_name, "Open", 0, "Welcome", 0, 0)
                    st.success(f"Added {new_name}!")
                    st.rerun()

        # C. TRANSACTION VIEW
        elif firm_sub_nav == "💸 Transaction":
            if not existing_clients:
                st.warning("Add a client first.")
            else:
                c_client = st.selectbox("Client", existing_clients)
                c_action = st.radio("Type", ["Deposit", "Withdrawal", "Penalty"], horizontal=True)
                c_amount = st.number_input("Amount", value=10.00)
                
                if c_action == "Deposit":
                    st.write(f"**Math Quiz:** 15% of ${c_amount}?")
                    guess = st.number_input("Your Math", value=0.0)
                    if st.button("Process Deposit"):
                        real_earn = round(c_amount * 0.15, 2)
                        client_save = c_amount - real_earn
                        note = "Deposit (Correct)" if abs(guess - real_earn) < 0.01 else "Deposit (Auto-Fixed)"
                        if abs(guess - real_earn) < 0.01: st.balloons()
                        save_client_transaction(c_client, "Deposit", c_amount, note, client_save, real_earn)
                        st.success("Done!")
                
                elif c_action == "Withdrawal":
                    if st.button("Process Withdrawal"):
                        save_client_transaction(c_client, "Withdrawal", c_amount, "Withdrawal", -c_amount, 0)
                        st.success("Done!")
                
                elif c_action == "Penalty":
                    if st.button("Charge Penalty"):
                        save_client_transaction(c_client, "Penalty", c_amount, "Late Fee", 0, c_amount)
                        st.success("Penalty Charged.")

    # ==========================
    # TAB 2: MY EMPIRE
    # ==========================
    with tab_empire:
        show_smart_banner("banner", "👛 My Empire")
        quote = get_daily_content(QUOTES_FILE, "DailyMotoQuote", "Secure the bag.")
        st.caption(f"Daily Wisdom: {quote}")
        
        # 2. SUB-NAVIGATION (Empire)
        empire_nav = st.radio("Menu:", ["🏆 Goals & Piggy", "💸 Money Mover", "📜 History"], horizontal=True, label_visibility="collapsed")
        st.markdown("---")
        
        personal_df = load_personal_data()
        goals_df = load_goals()
        client_df = load_client_data()
        
        total_earned = client_df["Niece_Earnings"].sum() if not client_df.empty else 0.0
        total_in_goals = goals_df["Balance"].sum()
        available_cash = total_earned + personal_df["Amount"].sum() - total_in_goals

        # A. GOALS
        if empire_nav == "🏆 Goals & Piggy":
            st.metric("💵 Available Cash", f"${available_cash:,.2f}")
            cols = st.columns(3)
            for index, row in goals_df.iterrows():
                with cols[index]:
                    st.markdown(f"### {row['Name']}")
                    percent = row['Balance'] / row['Target'] if row['Target'] > 0 else 0
                    st.progress(min(percent, 1.0))
                    st.write(f"${row['Balance']:.0f} / ${row['Target']:.0f}")
                    
                    pig_pic = get_pig_image(percent * 100)
                    if pig_pic: st.image(pig_pic, width=150)
            
            with st.expander("Edit Goals"):
                e_goal = st.selectbox("Goal", goals_df["Name"])
                new_n = st.text_input("New Name")
                new_t = st.number_input("New Target", value=100.0)
                if st.button("Update Goal"):
                    idx = goals_df.index[goals_df['Name'] == e_goal].tolist()[0]
                    goals_df.at[idx, 'Name'] = new_n if new_n else e_goal
                    goals_df.at[idx, 'Target'] = new_t
                    goals_df.to_csv(GOALS_FILE, index=False)
                    st.rerun()

        # B. MONEY MOVER
        elif empire_nav == "💸 Money Mover":
            st.subheader("Move Money")
            move_type = st.selectbox("Action", ["Deposit Cash (Gift)", "Spending", "Save to Goal", "Withdraw from Goal"])
            amt = st.number_input("Amount", value=10.0)
            
            if move_type == "Deposit Cash (Gift)":
                source = st.text_input("From who?", "Nana")
                if st.button("Add Cash"):
                    save_personal_transaction("Income", source, amt, get_sass("gift"))
                    st.balloons()
                    st.rerun()
            
            elif move_type == "Save to Goal":
                goal = st.selectbox("To Goal", goals_df["Name"])
                if st.button("Save"):
                    if amt <= available_cash:
                        update_goal(goal, amt)
                        save_personal_transaction("Savings Transfer", f"Saved to {goal}", 0, get_sass("saving"))
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Not enough cash.")

            elif move_type == "Spending":
                item = st.text_input("Item")
                if st.button("Spend"):
                    if amt <= available_cash:
                        save_personal_transaction("Spending", item, amt, get_sass("spending"))
                        st.rerun()
                    else:
                        st.error("No funds.")

        # C. HISTORY
        elif empire_nav == "📜 History":
            st.dataframe(personal_df.sort_index(ascending=False), use_container_width=True)

    # ==========================
    # TAB 3: BOSS MANUAL
    # ==========================
    with tab_help:
        st.title("❓ Boss Manual")
        st.markdown("""
        ### 1. The Firm
        - **Add Clients:** People who owe you money or want you to save it.
        - **Deposits:** When they give you cash, the system calculates your **15% cut**.
        
        ### 2. My Empire
        - **Piggy Bank:** As you save money into goals, the pig fills up with pink liquid!
        - **Available Cash:** This is your spending money.
        """)