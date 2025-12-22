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
    st.snow() 
    
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
# PART 2: THE BANKING APP
# ==========================================
else:
    df = load_data()

    # --- SIDEBAR: CLIENT MANAGEMENT ---
    st.sidebar.header("👥 Client Management")

    existing_clients = df["Client"].unique().tolist() if not df.empty else []
    menu_options = ["➕ Create New Client"] + existing_clients

    selected_option = st.sidebar.selectbox("Select Account", menu_options)
    
    # SAFEGUARD: Initialize current_client to None to prevent crashes
    current_client = None

    if selected_option == "➕ Create New Client":
        new_client_name = st.sidebar.text_input("Enter New Client Name:")
        if st.sidebar.button("Create Account"):
            if new_client_name and new_client_name not in existing_clients:
                save_transaction(new_client_name, "Account Open", 0, "Account Created", 0, 0)
                st.sidebar.success(f"Account for {new_client_name} created!")
                st.rerun()
        st.title("Welcome to Family Trust Bank")
        st.info("👈 Please create or select a client in the sidebar to begin.")
        
        # STOP HERE if we are creating a client. 
        # This prevents the code from trying to load data for a person who doesn't exist yet.
        st.stop() 
    else:
        current_client = selected_option

    # --- CALCULATE TOTALS ---
    # Only run the math if we actually have a client selected
    if current_client:
        total_earnings = df["Niece_Earnings"].sum()

        client_df = df[df["Client"] == current_client]
        if not client_df.empty:
            client_savings = client_df.iloc[-1]["Savings_Balance"]
        else:
            client_savings = 0.00

        st.sidebar.markdown("---")
        st.sidebar.header("📊 Financial Status")
        st.sidebar.metric("Your Total Earnings", f"${total_earnings:,.2f}", help="Total profit from all clients combined")
        st.sidebar.metric(f"{current_client}'s Savings", f"${client_savings:,.2f}", help=f"Money belonging to {current_client}")


        # --- MAIN AREA ---
        st.title(f"Managing: {current_client}")

        tab1, tab2, tab3 = st.tabs(["💵 Transactions", "📊 The Ledger", "🚨 Penalties"])

        with tab1:
            st.header(f"Transaction for {current_client}")
            action = st.radio("Action:", ["Bi-Weekly Deposit", "Borrow Money", "Repay Loan"], horizontal=True)
            st.markdown("---")

            # --- DEPOSIT WITH QUIZ ---
            if action == "Bi-Weekly Deposit":
                st.subheader("Step 1: Enter Details")
                amount = st.number_input("Deposit Amount ($)", value=10.00, step=1.00)
                
                st.subheader("Step 2: Accountant Pop Quiz 🧠")
                st.write(f"At **15%**, how much commission do you make from {current_client}?")
                
                user_guess = st.number_input("Your Calculation ($)", value=0.00, step=0.10)
                
                with st.expander("Need a math hint?"):
                    st.write("Formula: Deposit x 0.15")
                    st.code(f"{amount} x 0.15 = ?")

                if st.button("Submit Deposit"):
                    real_earnings = round(amount * 0.15, 2)
                    savings_deposit = amount - real_earnings
                    
                    if abs(user_guess - real_earnings) < 0.01:
                        st.balloons()
                        st.success(f"✅ Correct! You earned ${real_earnings:.2f}.")
                        note = "Regular Deposit (Math Correct)"
                    else:
                        st.warning(f"⚠️ Close! The math was: ${amount} × 0.15 = ${real_earnings:.2f}")
                        note = "Regular Deposit (Math Correction)"

                    save_transaction(current_client, "Deposit", amount, note, savings_deposit, real_earnings)
                    st.success(f"Added ${savings_deposit:.2f} to {current_client}'s savings.")
                    st.rerun()

            # --- BORROW MONEY ---
            elif action == "Borrow Money":
                amount = st.number_input("Borrow Amount", min_value=0.0)
                if amount > client_savings:
                    st.error(f"Insufficient Funds! {current_client} only has ${client_savings}")
                else:
                    if st.button("Process Loan"):
                        save_transaction(current_client, "Loan", amount, "Client Borrowed Money", -amount, 0)
                        st.success(f"Loan of ${amount} processed for {current_client}.")
                        st.rerun()

            # --- REPAY LOAN ---
            elif action == "Repay Loan":
                amount = st.number_input("Repayment Amount", min_value=0.0)
                if st.button("Process Repayment"):
                    save_transaction(current_client, "Repayment", amount, "Loan Repayment", amount, 0)
                    st.success(f"Loan Repaid by {current_client}!")
                    st.rerun()

        with tab2:
            st.header(f"History: {current_client}")
            st.dataframe(client_df.sort_index(ascending=False), use_container_width=True)

        with tab3:
            st.header("Late Penalty Calculator")
            days = st.number_input("Days Late", min_value=1, step=1)
            
            st.subheader("Pop Quiz 🧠")
            st.write(f"Calculate penalty for {days} days late ($5/day).")
            penalty_guess = st.number_input("Your Penalty Calculation ($)", value=0.0, step=1.0)
            
            if st.button("Charge Penalty"):
                real_penalty = days * 5.00
                
                if abs(penalty_guess - real_penalty) < 0.01:
                    st.success("✅ Correct!")
                    st.balloons()
                else:
                    st.warning(f"⚠️ Close! Correct amount is ${real_penalty:.2f}.")
                    
                save_transaction(current_client, "Penalty", real_penalty, f"Late Fee ({days} days)", 0, real_penalty)
                st.success(f"Penalty charged to {current_client}.")