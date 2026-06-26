import streamlit as st
import pandas as pd

# Google Sheet ID
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
URL_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"

# --- INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "role" not in st.session_state: st.session_state.role = None
if "username" not in st.session_state: st.session_state.username = None

def load_users():
    try:
        df = pd.read_csv(URL_USERS)
        return dict(zip(df['Username'].astype(str), df['Password'].astype(str)))
    except:
        return {}

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Exam Terminal")
    users = load_users()
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        elif user in users and pwd == users[user]:
            st.session_state.logged_in = True
            st.session_state.role = "student"
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Invalid Login")
else:
    # --- ADMIN PANEL ---
    if st.session_state.role == "admin":
        st.title("👩‍🏫 Admin Control Panel")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()
        # Sheet1 ကို ပြသခြင်း
        url_results = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
        try:
            st.table(pd.read_csv(url_results))
        except:
            st.write("Results မရှိသေးပါ။")
    
    # --- STUDENT PANEL ---
    else:
        st.title(f"✍️ Welcome, {st.session_state.username}")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()
        st.write("စာမေးပွဲဖြေဆိုရန် အဆင်သင့်ဖြစ်ပါပြီ။")
