import streamlit as st
import pandas as pd

# 1. Configuration - Google Sheet ID (ဆရာ့ Sheet ID အမှန်ဖြစ်ပါစေ)
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
URL_RESULTS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
URL_QUESTIONS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"
URL_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"

# 2. Session State Initialization
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "role" not in st.session_state: st.session_state.role = None
if "username" not in st.session_state: st.session_state.username = None

# 3. Data Loading Functions (Cache ပိတ်ထားခြင်းဖြင့် Live data ပေါ်စေမည်)
def load_data(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# 4. App Logic
if not st.session_state.logged_in:
    st.title("🔐 Secure Exam Terminal")
    df_users = load_data(URL_USERS)
    
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Admin Login
        if user == "admin" and pwd == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        # Student Login
        elif not df_users.empty and user in df_users['Username'].values:
            actual_pwd = str(df_users[df_users['Username'] == user]['Password'].values[0])
            if str(pwd) == actual_pwd:
                st.session_state.logged_in = True
                st.session_state.role = "student"
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Invalid Password!")
        else:
            st.error("Invalid Username!")

else:
    # --- ADMIN VIEW ---
    if st.session_state.role == "admin":
        st.title("👩‍🏫 Admin Control Panel")
        if st.button("Log out"): st.session_state.logged_in = False; st.rerun()
        if st.button("Refresh Results"): st.rerun()
        # ဒေတာဇယားပြသခြင်း
        df_res = load_data(URL_RESULTS)
        st.table(df_res)
    
# --- STUDENT VIEW ---
    else:
        st.title(f"✍️ Welcome, {st.session_state.username}")
        if st.button("Log out"): st.session_state.logged_in = False; st.rerun()
        
        # ဒေတာကို ဖတ်ပါ
        questions = load_data(URL_QUESTIONS)
        
        # Debugging: ဒေတာဘာတွေပါလဲ စစ်ဆေးခြင်း
        st.write("Debug: Loaded Questions Data:")
        st.write(questions) # ဒီနေရာမှာ မေးခွန်းတွေ ပေါ်မလာရင် URL မှာ ပြဿနာရှိနေတာပါ
        
        if not questions.empty:
            st.table(questions)
        else:
            st.warning("မေးခွန်းများ မတွေ့ရှိပါ။ Google Sheet link သို့မဟုတ် Sheet2 ကို ပြန်စစ်ပါ။")
