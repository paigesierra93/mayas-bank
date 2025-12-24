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
FACTS_FILE = "facts.csv"
PIG_FILE = "pig_map.csv"

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

# --- HELPER: FIND BANNER IMAGE ---
def show_smart_banner(base_name, fallback_title):
    # This checks for banner.png, Banner.png, banner.jpg, etc.
    possible_files = [
        f"{base_name}.png", f"{base_name}.PNG",
        f"{base_name}.jpg", f"{base_name}.JPG",
        f"{base_name}.jpeg"
    ]
    
    found = False
    for f in possible_files:
        if os.path.exists(f):
            st.image(f, use_container_width=True)
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
    .fact-card { background-color: #1c1e26; padding: 40px; border-radius: 15px; border: 2px solid #ff4b4b; text-align: center; margin-bottom: 20px; }
    .history-card { background-color: #1c1e26; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #555; }
    .pos { border-left-color: #00cc00; }
    .neg { border-left-color: #ff4444; }
    .gold { border-left-color: #ffd700; }
    .tutorial-box { background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #555; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- INTRO LOGIC ---
if 'intro_seen' not in st.session_state:
    st.session_state['intro_seen'] = False

if not st.session_state['intro_seen']:
    is_first_run = not os.path.exists(CLIENT_FILE)
    if is_first_run:
        st.snow()
        st.markdown('<div class="fact-card">', unsafe_allow_html=True)
        st.title("🎄 Merry Christmas, Maya! 🎄")
        st.write("### To my beautiful and smart niece,")
        st.write("""
        I've created this software for you so you can begin your journey into your future. 
        You have such a bright path ahead of you in accounting, and every accountant needs 
        their first set of books.
        
        I hope this tool will help you learn how money grows, how to track clients, 
        and how to build your own wealth.
        
        Love, Aunt Paige
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("🚀 Launch My Accounting System", type="primary"):
            st.session_state['intro_seen'] = True
            st.rerun()
    else:
        daily_fact = get_daily_content(FACTS_FILE, "Fun Fact", "Accountants are the rock stars of business.")
        st.markdown('<div class="fact-card">', unsafe_allow_html=True)
        st.title("🧠 Accountant Fact of the Day")
        st.write(f"### {daily_fact}")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("✨ Enter Empire Mode ✨", type="primary"):
            st.session_state['intro_seen'] = True
            st.rerun()

# --- MAIN APP ---
else:
    st.sidebar.title("💅 Navigation")
    mode = st.sidebar.radio("Go to:", ["💼 The Firm (Clients)", "👛 My Empire (Budget)", "❓ How to Use (Tutorial)"])

    # 1. THE FIRM
    if mode == "💼 The Firm (Clients)":
        
        # Smart Check for Firm Banner (firm_banner.png, firm_banner.jpg, etc.)
        show_smart_banner("firm_banner", "💼 The Firm: Client Management")

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

    # 2. MY EMPIRE
    elif mode == "👛 My Empire (Budget)":
        quote = get_daily_content(QUOTES_FILE, "DailyMotoQuote", "Secure the bag.")
        st.toast(f"✨ Daily Vibe: {quote}")
        
        # Smart Check for Empire Banner (banner.png, banner.jpg, etc.)
        show_smart_banner("banner", "👛 My Empire")
            
        st.markdown(f'<div class="quote-box">📅 <strong>Daily Wisdom:</strong> "{quote}"</div>', unsafe_allow_html=True)

        client_df = load_client_data()
        personal_df = load_personal_data()
        goals_df = load_goals()
        
        total_earned = client_df["Niece_Earnings"].sum() if not client_df.empty else 0.0
        total_in_goals = goals_df["Balance"].sum()
        available_cash = total_earned + personal_df["Amount"].sum() - total_in_goals

        st.subheader("🏆 The Goal Tracker")
        cols = st.columns(3)
        goal_names = goals_df["Name"].tolist()
        for index, row in goals_df.iterrows():
            with cols[index]:
                st.markdown(f"### {row['Name']}")
                
                percent = 0.0
                if row['Target'] > 0:
                    percent = row['Balance'] / row['Target']
                
                st.progress(min(percent, 1.0))
                st.write(f"**${row['Balance']:,.0f}** / ${row['Target']:,.0f}")
                
                pig_pic = get_pig_image(percent * 100)
                if pig_pic and os.path.exists(pig_pic):
                    st.image(pig_pic, width=150)
                
                if percent >= 1.0: st.success("GOAL MET! 🎉")
        
        with st.expander("⚙️ Edit Goal Details"):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                edit_goal = st.selectbox("Select Goal to Edit", goal_names)
            with col_e2:
                current_row = goals_df[goals_df["Name"] == edit_goal].iloc[0]
                new_n = st.text_input("Rename Goal:", value=current_row["Name"])
                new_t = st.number_input("Change Target ($):", value=float(current_row["Target"]))
                if st.button("Update Goal Settings"):
                    idx = goals_df.index[goals_df['Name'] == edit_goal].tolist()[0]
                    goals_df.at[idx, 'Name'] = new_n
                    goals_df.at[idx, 'Target'] = new_t
                    goals_df.to_csv(GOALS_FILE, index=False)
                    st.success(f"Updated {edit_goal}!")
                    st.rerun()

        st.markdown("---")
        st.subheader("💸 Money Mover")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.metric("💵 Cash Available", f"${available_cash:,.2f}")
            move_type = st.radio("What are we doing?", 
                                 ["➕ Deposit Cash (Gift/Allowance)", 
                                  "💸 Spending (Buying Stuff)", 
                                  "🐷 Saving (Stashing Cash)", 
                                  "↩️ Return / Refund (Undo Spending)", 
                                  "🔓 Withdraw from Savings (Use Goal Money)"])
            
            amount = st.number_input("Amount ($)", min_value=0.01, value=10.00)

            if "Deposit Cash" in move_type:
                source_desc = st.text_input("From who?", value="Nana")
                if st.button("Add Cash 💵"):
                    save_personal_transaction("Income", source_desc, amount, get_sass("gift"))
                    st.balloons()
                    st.rerun()

            elif "Spending" in move_type:
                item = st.text_input("What did you buy?")
                if st.button("Buy it 🛍️"):
                    if amount > available_cash: st.error("Insufficient funds.")
                    else:
                        save_personal_transaction("Spending", item, amount, get_sass("spending"))
                        st.rerun()

            elif "Saving" in move_type:
                target_goal = st.selectbox("Which Goal?", goal_names)
                if st.button("Stash it 💰"):
                    if amount > available_cash: st.error("Not enough cash.")
                    else:
                        update_goal(target_goal, amount)
                        save_personal_transaction("Savings Transfer", f"Saved to {target_goal}", 0, get_sass("saving"))
                        st.balloons()
                        st.rerun()

            elif "Return" in move_type:
                item = st.text_input("What did you return?")
                if st.button("Process Refund"):
                    save_personal_transaction("Refund", item, amount, get_sass("refund"))
                    st.success("Refund processed!")
                    st.rerun()

            elif "Withdraw from Savings" in move_type:
                source_goal = st.selectbox("Take from which goal?", goal_names)
                if st.button("Withdraw"):
                    goal_row = goals_df[goals_df["Name"] == source_goal].iloc[0]
                    if amount > goal_row["Balance"]: st.error("Not enough funds.")
                    else:
                        if goal_row["Balance"] >= goal_row["Target"]:
                            update_goal(source_goal, -amount)
                            save_personal_transaction("Reward", f"Cashed out {source_goal}", amount, get_sass("goal_hit"))
                            st.session_state['recycle_mode'] = source_goal
                            st.experimental_rerun()
                        else:
                            update_goal(source_goal, -amount)
                            save_personal_transaction("Early Withdrawal", f"Took from {source_goal}", 0, get_sass("early_withdraw"))
                            st.rerun()
            
            if 'recycle_mode' in st.session_state:
                old_name = st.session_state['recycle_mode']
                st.info(f"♻️ Recycling '{old_name}'!")
                new_n = st.text_input("New Name (Recycle)", value="New Goal")
                new_t = st.number_input("New Target (Recycle)", value=500.0)
                if st.button("Set New Goal (Recycle)"):
                    reset_goal(old_name, new_n, new_t)
                    del st.session_state['recycle_mode']
                    st.rerun()
        
        with c2:
            st.write("### 📜 Transaction Feed")
            if not personal_df.empty:
                for index, row in personal_df.sort_index(ascending=False).iterrows():
                    amt = row['Amount']
                    css_class = "pos"
                    display_amt = f"+${abs(amt):.2f}"
                    
                    if amt < 0:
                        css_class = "neg"
                        display_amt = f"-${abs(amt):.2f}"
                    elif row['Category'] == "Reward":
                        css_class = "gold"
                        display_amt = f"+${abs(amt):.2f} (Reward)"
                    
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

    # 3. TUTORIAL PAGE
    elif mode == "❓ How to Use (Tutorial)":
        st.title("❓ The Boss Manual")
        st.markdown("Everything you need to know to run your empire.")
        
        st.markdown("""
        <div class="tutorial-box">
        <h3>1. 💼 The Firm (Making Money)</h3>
        <p>This is where you act as the Accountant for clients (like your family).</p>
        <ul>
            <li><strong>Add Clients:</strong> Use the sidebar to add "Mom", "Dad", etc.</li>
            <li><strong>Incoming Deposit:</strong> When they give you money to save, enter it here.</li>
            <li><strong>The 15% Rule:</strong> The app <em>automatically</em> calculates your 15% fee. 
                If they give you $100, $15 goes to YOU, and $85 goes to THEM.</li>
            <li><strong>Penalties:</strong> If they are late, charge them! This money goes 100% to you.</li>
        </ul>
        </div>
        
        <div class="tutorial-box">
        <h3>2. 👛 My Empire (Your Stash)</h3>
        <p>This is your personal wallet. All your earnings from The Firm show up here automatically.</p>
        <ul>
            <li><strong>Available Cash:</strong> This is money in your pocket ready to be spent or saved.</li>
            <li><strong>Goal Tracker:</strong> You have 3 savings buckets (Car, College, etc).</li>
            <li><strong>The Pig:</strong> As you fill a goal, the pig picture will fill up with pink liquid! 🐷</li>
        </ul>
        </div>

        <div class="tutorial-box">
        <h3>3. 💸 The Money Mover</h3>
        <p>This is how you move cash around in "My Empire".</p>
        <ul>
            <li><strong>➕ Deposit Cash:</strong> Use this for gifts (like $20 from Nana). It adds straight to your cash.</li>
            <li><strong>💸 Spending:</strong> Use this when you buy something (Starbucks, Makeup). It subtracts from cash.</li>
            <li><strong>🐷 Saving:</strong> Moves money from "Available Cash" into a "Goal". Watch the pig grow!</li>
            <li><strong>🔓 Withdraw from Savings:</strong> Takes money OUT of a goal back to cash. 
                <em>Warning: If you do this before the goal is full, the app will judge you.</em></li>
        </ul>
        </div>

        <div class="tutorial-box">
        <h3>4. ♻️ Recycling Goals</h3>
        <p>When you hit 100% on a goal (like reaching $500 for a trip):</p>
        <ul>
            <li>Withdraw the money to spend it!</li>
            <li>The app will ask if you want to <strong>"Recycle"</strong> the goal.</li>
            <li>You can rename it to something new (e.g., change "Trip" to "Laptop") and start saving again!</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)