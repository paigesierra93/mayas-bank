import streamlit as st
import pandas as pd
import os
import random
import base64
import re
from datetime import datetime
import google.generativeai as genai
import warnings
import glob
import time

# --- 1. SILENCE WARNINGS ---
warnings.filterwarnings("ignore")
os.environ["STREAMLIT_SILENCE_DEPRECATION_WARNING"] = "1"

# --- PAGE CONFIG (MOBILE OPTIMIZED) ---
st.set_page_config(
    page_title="Mathletes & Plastics", 
    page_icon="💋", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FILE & FOLDER SETUP ---
CLIENT_FILE = "ledger.csv"
PERSONAL_FILE = "my_budget.csv"
GOALS_FILE = "goals.csv"
QUOTES_FILE = "quotes.csv"
GIF_DIR = "gifs"

# --- IMAGE HELPERS ---
def get_base64_image(image_path):
    # Try exact match first
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    
    # Try Uppercase/Lowercase variations (Linux is picky!)
    alt_paths = [image_path.lower(), image_path.upper(), image_path.replace(".jpg", ".JPG"), image_path.replace(".png", ".PNG")]
    for p in alt_paths:
        if os.path.exists(p):
            with open(p, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
            
    return ""

# --- LOAD IMAGES (THE FIX) ---
bg_menu = get_base64_image("menu_background.jpg")
bg_math = get_base64_image("north_shore.jpg")
bg_plastic = get_base64_image("burn_book_background.png") # Make sure this matches your file name!

# --- DATA LOADING ---
def load_client_data():
    if not os.path.exists(CLIENT_FILE):
        return pd.DataFrame(columns=["Date", "Client", "Type", "Amount", "Note", "Savings_Balance", "Niece_Earnings", "Target"])
    df = pd.read_csv(CLIENT_FILE)
    if "Target" not in df.columns: df["Target"] = 0.0
    return df

def load_personal_data():
    if not os.path.exists(PERSONAL_FILE):
        return pd.DataFrame(columns=["Date", "Category", "Item", "Amount", "Sass_Level"])
    return pd.read_csv(PERSONAL_FILE)

def load_goals():
    if not os.path.exists(GOALS_FILE):
        data = {"Name": ["Spring Fling Dress", "College", "Pink Jeep"], "Target": [1000.0, 5000.0, 300.0], "Balance": [0.0, 0.0, 0.0]}
        df = pd.DataFrame(data)
        df.to_csv(GOALS_FILE, index=False)
        return df
    return pd.read_csv(GOALS_FILE)

def get_daily_content(file_path, column_name, fallback):
    if not os.path.exists(file_path): return fallback
    try:
        df = pd.read_csv(file_path)
        day = datetime.now().timetuple().tm_yday
        return df.iloc[(day - 1) % len(df)][column_name]
    except: return fallback

# --- CORE LOGIC ---
def save_personal_transaction(category, item, amount, sass):
    df = load_personal_data()
    if category in ["Spending", "Withdrawal", "Transfer"] and amount > 0: 
        amount = -amount
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Category": category, 
        "Item": item, "Amount": amount, "Sass_Level": sass
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(PERSONAL_FILE, index=False)

def save_client_transaction(client_name, type, amount, note, savings_change, earnings_change, target=0.0):
    df = load_client_data()
    old_bal = 0.0
    client_rows = df[df["Client"] == client_name]
    if not client_rows.empty: old_bal = client_rows.iloc[-1]["Savings_Balance"]
    
    new_entry = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
        "Client": client_name, 
        "Type": type, 
        "Amount": amount, 
        "Note": note, 
        "Savings_Balance": round(old_bal + savings_change, 2), 
        "Niece_Earnings": earnings_change, 
        "Target": target
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CLIENT_FILE, index=False)
    
    if earnings_change > 0:
        save_personal_transaction("Income", f"Business: {client_name}", earnings_change, "Hustle")

def update_goal(goal_name, amount_change):
    df = load_goals()
    matches = [name for name in df['Name'] if goal_name.lower() in name.lower()]
    if matches:
        target_goal = matches[0]
        idx = df.index[df['Name'] == target_goal].tolist()[0]
        df.at[idx, 'Balance'] += amount_change
        df.to_csv(GOALS_FILE, index=False)
        return target_goal
    return None

# --- PARSING ---
def process_plastics_command(text):
    text = text.lower()
    match_spend = re.search(r'(spend|bought|buy|spent)\s?\$?(\d+(\.\d+)?)\s?(on|for)?\s(.+)', text)
    if match_spend:
        amt = float(match_spend.group(2))
        item = match_spend.group(5)
        pdf = load_personal_data()
        cash = pdf["Amount"].sum()
        if amt > cash: return False, f"Insufficient funds to spend ${amt}."
        save_personal_transaction("Spending", item, amt, "Chat Command")
        return True, f"Logged purchase: {item} for ${amt}."
    
    match_inc = re.search(r'(add|got|deposit|income)\s?\$?(\d+(\.\d+)?)\s?(from)?\s(.+)', text)
    if match_inc:
        amt = float(match_inc.group(2))
        source = match_inc.group(5)
        save_personal_transaction("Income", source, amt, "Chat Command")
        return True, f"Added ${amt} from {source}."
        
    match_save = re.search(r'(save|move|transfer)\s?\$?(\d+(\.\d+)?)\s?(to|for)\s(.+)', text)
    if match_save:
        amt = float(match_save.group(2))
        goal_input = match_save.group(5)
        pdf = load_personal_data()
        cash = pdf["Amount"].sum()
        if amt > cash: return False, "Insufficient funds."
        updated_name = update_goal(goal_input, amt)
        if updated_name:
            save_personal_transaction("Transfer", f"To {updated_name}", amt, "Chat Command")
            return True, f"Moved ${amt} to {updated_name}."
    return False, None

def process_mathletes_command(text):
    text = text.lower()
    match_new = re.search(r'new client\s(\w+)\sgoal\s\$?(\d+)', text)
    if match_new:
        name = match_new.group(1).capitalize(); goal = float(match_new.group(2))
        save_client_transaction(name, "Joined", 0, "Chat", 0, 0, goal)
        return True, f"Created file: {name}."
        
    df = load_client_data()
    existing_clients = [c.lower() for c in df["Client"].unique()]
    target = None
    for c in existing_clients:
        if c in text: target = df[df["Client"].str.lower() == c].iloc[0]["Client"]; break
    
    if not target: return False, None
    
    match_dep = re.search(r'(deposit|add)\s\$?(\d+(\.\d+)?)', text)
    if match_dep:
        amt = float(match_dep.group(2))
        real = round(amt*0.85, 2); profit = round(amt*0.15, 2)
        save_client_transaction(target, "Deposit", amt, "Chat", real, profit)
        return True, f"Deposited ${amt} for {target}."
        
    match_pen = re.search(r'(charge|penalty)\s\$?(\d+(\.\d+)?)', text)
    if match_pen:
        amt = float(match_pen.group(2))
        save_client_transaction(target, "Penalty", amt, "Chat", 0, amt)
        return True, f"Charged ${amt} penalty to {target}."
        
    return False, None

# --- GIFS ---
def show_sass_gif(category):
    target = os.path.join(GIF_DIR, category)
    if os.path.exists(target):
        files = [f for f in os.listdir(target) if f.lower().endswith(('.gif', '.jpg', '.png'))]
        if files: st.image(os.path.join(target, random.choice(files)), width=300)

# --- AI BRAIN ---
def get_ai_reply(persona, prompt, context="", action_report=""):
    if not st.session_state.api_key: return "Enter the API key in the sidebar first."
    genai.configure(api_key=st.session_state.api_key)
    model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    if "Regina" in persona:
        system_prompt = f"""You are REGINA GEORGE. CONTEXT: {context}. ACTION REPORT: "{action_report}". USER SAYS: "{prompt}". 
        INSTRUCTIONS: If action done, complain about labor but confirm. Judge spending. Be sassy/mean. Short."""
    else:
        system_prompt = f"""You are KEVIN GNAPOOR. CONTEXT: {context}. ACTION REPORT: "{action_report}". USER SAYS: "{prompt}". 
        INSTRUCTIONS: If action done, confirm with math slang. If question, give 1-sentence math lesson. Short."""

    for m in model_candidates:
        try:
            model = genai.GenerativeModel(m)
            return model.generate_content(system_prompt).text
        except: continue
    return "Internet broken."

# --- CSS (VISUAL REPAIR) ---
# This CSS puts the images back into the backgrounds!
st.markdown(f"""
<style>
    /* 1. RESTORE SIDEBAR IMAGE */
    [data-testid="stSidebar"] {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_menu}");
        background-size: cover; 
        background-position: center;
        background-color: #000; /* Fallback if image missing */
        border-right: 3px solid #FF1493;
    }}
    [data-testid="stSidebar"] * {{ color: white !important; text-shadow: 1px 1px 2px black; }}
    
    /* 2. RESTORE MATH BACKGROUND */
    .math-container {{
        background-image: linear-gradient(rgba(255, 249, 196, 0.9), rgba(255, 249, 196, 0.9)), url("data:image/jpeg;base64,{bg_math}");
        background-size: cover;
        background-color: #FFF9C4; /* Fallback */
        border: 4px solid #1A237E; padding: 15px; border-radius: 10px; color: black;
    }}
    
    /* 3. RESTORE PLASTICS BACKGROUND */
    .plastic-container {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), url("data:image/png;base64,{bg_plastic}");
        background-size: cover;
        background-color: #FCE4EC; /* Fallback */
        border: 4px solid #FF1493; padding: 15px; border-radius: 0px; color: black;
    }}

    /* 4. FIX THE TABS (MAKE THEM POP) */
    button[data-baseweb="tab"] {{
        font-size: 20px !important;
        font-weight: bold !important;
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 5px 5px 0 0;
        margin-right: 5px;
    }}
    div[data-baseweb="tab-list"] {{ gap: 10px; }}
    
    /* CHAT BUBBLES */
    .bubble {{ padding: 10px 15px; border-radius: 15px; max-width: 85%; font-family: sans-serif; font-size: 14px; margin-bottom: 5px; }}
    .bubble-math {{ background: #E8EAF6; border: 2px solid #1A237E; color: black; float: left; clear: both; }}
    .bubble-plastic {{ background: #FFF0F5; border: 2px solid #D81B60; color: black; float: left; clear: both; }}
    .bubble-user {{ background: #333; color: white; border: 2px solid black; float: right; clear: both; text-align: right; }}
    .chat-row {{ overflow: hidden; margin-bottom: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'api_key' not in st.session_state: st.session_state.api_key = ""
if 'math_history' not in st.session_state: st.session_state.math_history = [{"role": "assistant", "content": "Kevin G here. Stats are looking tight."}]
if 'plastic_history' not in st.session_state: st.session_state.plastic_history = [{"role": "assistant", "content": "Get in loser, we're doing finances."}]
if 'math_tut_step' not in st.session_state: st.session_state.math_tut_step = 0
if 'plastic_tut_step' not in st.session_state: st.session_state.plastic_tut_step = 0

# --- SMART LOGIN ---
if "google" in st.secrets:
    st.session_state.api_key = st.secrets["google"]["api_key"]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1>🔥 MAYA'S<br>BURN BOOK</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**Today's Gossip:**\n\n_{get_daily_content(QUOTES_FILE, 'Quote', 'On Wednesdays we wear pink.')}_")
    
    if not st.session_state.api_key:
        user_key = st.text_input("Enter Password (API)", type="password")
        if user_key: st.session_state.api_key = user_key
    else:
        st.success("✅ AI Access Granted")

    st.divider()
    if st.button("☁️ Sync to Cloud (Save)"):
        try:
            from github import Github
            token = st.secrets["github"]["token"]
            repo_name = st.secrets["github"]["repo_name"]
            g = Github(token)
            repo = g.get_repo(repo_name)
            
            status_text = st.empty()
            status_text.text("⏳ Scanning files...")
            files_to_save = glob.glob("*.csv") 
            
            for file_path in files_to_save:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f: content = f.read()
                    try:
                        contents = repo.get_contents(file_path)
                        repo.update_file(contents.path, f"Update {file_path}", content, contents.sha)
                    except:
                        repo.create_file(file_path, f"Create {file_path}", content)
            
            st.success(f"✅ Synced {len(files_to_save)} files!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Save Failed: {e}")

if not st.session_state.api_key:
    st.markdown("<div style='text-align:center; margin-top:20%; font-family:Arial Black; font-size: 50px;'>LOCKED.</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# MAIN APP
# ==========================================
# This creates the tabs at the top. 
# They might be white-on-white, but the CSS above fixes that!
tab_math, tab_plastic = st.tabs(["📘 Mathletes", "💖 The Plastics"])

# --- TAB 1: MATHLETES ---
with tab_math:
    st.markdown('<div class="math-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#1A237E; text-align:right; border-bottom:3px solid #1A237E;">MATHLETES: CLIENT MANAGEMENT</h2>', unsafe_allow_html=True)
    
    # RESTORED TUTORIAL LOGIC
    if st.session_state.math_tut_step == 1:
        st.info("🎓 TUTORIAL: Step 1")
        if st.button("Next >"): 
            st.session_state.math_history.append({"role": "assistant", "content": "Yo, check the CHAT below. You can tell me 'Deposit 50 for Mom' or 'New Client Sam'. I handle the math."})
            st.session_state.math_tut_step = 2; st.rerun()
    elif st.session_state.math_tut_step == 2:
        st.info("🎓 TUTORIAL: Step 2")
        if st.button("Next >"): 
            st.session_state.math_history.append({"role": "assistant", "content": "Below the chat are the TOOLS. Use 'New File' to add people. Use 'Audit' to charge penalties."})
            st.session_state.math_tut_step = 3; st.rerun()
    elif st.session_state.math_tut_step == 3:
        st.info("🎓 TUTORIAL: Finished")
        if st.button("End Class"): 
            st.session_state.math_history.append({"role": "assistant", "content": "Lesson over. Get back to work."})
            st.session_state.math_tut_step = 0; st.rerun()

    # CHAT
    with st.container(height=300):
        for msg in st.session_state.math_history:
            css = "bubble-user" if msg["role"] == "user" else "bubble-math"
            st.markdown(f'<div class="chat-row"><div class="bubble {css}">{msg["content"]}</div></div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask Kevin...", key="m_in"):
        st.session_state.math_history.append({"role": "user", "content": prompt})
        success, report = process_mathletes_command(prompt)
        if success: show_sass_gif("good")
        df = load_client_data()
        context = f"Clients: {df['Client'].unique().tolist()}. Revenue: ${df['Niece_Earnings'].sum():.2f}."
        reply = get_ai_reply("Kevin Gnapoor", prompt, context, report if success else "")
        st.session_state.math_history.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("---")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("🆕 New File"): st.session_state.m_mode = "New"
    if c2.button("📂 Audit"): st.session_state.m_mode = "Audit"
    if c3.button("📜 Logs"): st.session_state.m_mode = "View"
    if c4.button("🎓 School"): 
        st.session_state.m_mode = "None"
        st.session_state.math_tut_step = 1
        st.session_state.math_history.append({"role": "assistant", "content": "Alright class, listen up."})
        st.rerun()
    if c5.button("🔄 Clear"): st.session_state.m_mode = "None"
    
    mode = getattr(st.session_state, 'm_mode', 'None')
    if mode == "New":
        with st.form("new_c"):
            name = st.text_input("Name"); goal = st.number_input("Goal", 100.0)
            if st.form_submit_button("Create"):
                save_client_transaction(name, "Joined", 0, "Chat", 0, 0, goal)
                st.success("Created"); show_sass_gif("save")
    elif mode == "Audit":
        df = load_client_data(); clients = df["Client"].unique()
        if len(clients) > 0:
            target = st.selectbox("Client", clients)
            ac1, ac2, ac3 = st.columns(3)
            if ac1.button("Deposit"): 
                val = st.number_input("Amt", 0.01); 
                if st.button("Go"): save_client_transaction(target, "Deposit", val, "Man", val*0.85, val*0.15); st.success("Done")
            if ac2.button("Penalty"):
                val = st.number_input("Fee", 5.0); 
                if st.button("Charge"): save_client_transaction(target, "Penalty", val, "Man", 0, val); st.success("Done")
    elif mode == "View":
        df = load_client_data(); target = st.selectbox("View", df["Client"].unique())
        st.dataframe(df[df["Client"]==target])

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: PLASTICS ---
with tab_plastic:
    st.markdown('<div class="plastic-container">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#D81B60; text-align:center; border-bottom:3px solid black; font-family:Brush Script MT, cursive; font-size:40px;">💋 THE BURN BOOK (FINANCES)</h2>', unsafe_allow_html=True)
    
    # RESTORED TUTORIAL LOGIC
    if st.session_state.plastic_tut_step == 1:
        st.info("🎓 TUTORIAL: Step 1")
        if st.button("Next >", key="p_next1"): 
            st.session_state.plastic_history.append({"role": "assistant", "content": "Okay, look at the CHAT. You can tell me 'Spend 50 on shoes' or 'Add 20 from Nana'. I'll handle the rest."})
            st.session_state.plastic_tut_step = 2; st.rerun()
    elif st.session_state.plastic_tut_step == 2:
        st.info("🎓 TUTORIAL: Step 2")
        if st.button("Next >", key="p_next2"): 
            st.session_state.plastic_history.append({"role": "assistant", "content": "Down there are the BUTTONS. Spend, Save, Income. Use them if you're too lazy to type."})
            st.session_state.plastic_tut_step = 3; st.rerun()
    elif st.session_state.plastic_tut_step == 3:
        st.info("🎓 TUTORIAL: Finished")
        if st.button("Finish", key="p_fin"): 
            st.session_state.plastic_history.append({"role": "assistant", "content": "That's it. Don't be poor."})
            st.session_state.plastic_tut_step = 0; st.rerun()

    with st.container(height=300):
        for msg in st.session_state.plastic_history:
            css = "bubble-user" if msg["role"] == "user" else "bubble-plastic"
            st.markdown(f'<div class="chat-row"><div class="bubble {css}">{msg["content"]}</div></div>', unsafe_allow_html=True)

    if prompt_p := st.chat_input("Tell Regina...", key="p_in"):
        st.session_state.plastic_history.append({"role": "user", "content": prompt_p})
        success, report = process_plastics_command(prompt_p)
        if success: show_sass_gif("spend")
        pdf = load_personal_data(); goals = load_goals()
        context = f"Cash: ${pdf['Amount'].sum():.2f}. Goals: {goals.to_dict('records')}."
        reply_p = get_ai_reply("Regina George", prompt_p, context, report if success else "")
        st.session_state.plastic_history.append({"role": "assistant", "content": reply_p})
        st.rerun()

    st.markdown("---")
    st.metric("🍸 LIQUID CASH", f"${load_personal_data()['Amount'].sum():.2f}")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    if c1.button("🛍️ Spend"): st.session_state.p_tool = "Spend"
    if c2.button("🐷 Save"): st.session_state.p_tool = "Save"
    if c3.button("💵 Income"): st.session_state.p_tool = "Income"
    if c4.button("🔥 Ledger"): st.session_state.p_tool = "Edit"
    if c5.button("🎯 Goals"): st.session_state.p_tool = "Goals"
    if c6.button("🎓 Guide"): 
        st.session_state.p_tool = "None"
        st.session_state.plastic_tut_step = 1
        st.session_state.plastic_history.append({"role": "assistant", "content": "Ugh, fine."})
        st.rerun()

    ptool = getattr(st.session_state, 'p_tool', None)
    if ptool == "Spend":
        amt = st.number_input("Amt", 0.01); item = st.text_input("Item")
        if st.button("Buy"): save_personal_transaction("Spending", item, amt, "Yolo"); st.success("Bought"); st.rerun()
    elif ptool == "Save":
        amt = st.number_input("Amt", 0.01); sel = st.selectbox("Goal", load_goals()["Name"])
        if st.button("Transfer"): 
            update_goal(sel, amt); save_personal_transaction("Transfer", f"To {sel}", amt, "Smart"); st.success("Saved"); st.rerun()
    elif ptool == "Income":
        amt = st.number_input("Amt", 0.01); src = st.text_input("Source")
        if st.button("Add"): save_personal_transaction("Income", src, amt, "Job"); st.success("Added"); st.rerun()
    elif ptool == "Edit":
        st.data_editor(load_personal_data(), num_rows="dynamic")
    elif ptool == "Goals":
        st.data_editor(load_goals(), num_rows="dynamic")

    st.markdown("---")
    st.write("### 🏆 GOALS")
    for i, row in load_goals().iterrows():
        st.write(f"**{row['Name']}**: ${row['Balance']:.0f} / ${row['Target']:.0f}")
        st.progress(min(row['Balance']/row['Target'] if row['Target']>0 else 0, 1.0))

    st.markdown('</div>', unsafe_allow_html=True)