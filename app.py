import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.request
import json
import time

# --- CONFIG & URLS ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwyFMXmqgLQyIx-kUN54Q5oVV4q8T1WJEvoksyo_EugBLAYeZ9SUQt35BpQF8pWMOmbcQ/exec"
EXAM_DURATION_MINUTES = 20

# --- HELPER FUNCTIONS ---
def get_mm_now():
    return datetime.utcnow() + timedelta(hours=6, minutes=30)

if "global_results_pool" not in st.session_state: st.session_state.global_results_pool = []

def get_results_from_sheet():
    try: return pd.read_csv(CSV_RESULTS_URL).values.tolist()
    except: return []

# --- APP LAYOUT ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Secure Login", type="primary"):
        # Login logic (simplified for brevity)
        st.session_state.logged_in = True
        st.session_state.user_role = "admin" if username == "admin" else "student"
        st.session_state.username = username
        st.rerun()
else:
    # Sidebar Logout (One place only!)
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # Admin Panel
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel")
        st.sidebar.subheader("⚙️ System Control")
        if st.sidebar.button("♻️ FULL SYSTEM RESET", type="primary"):
            st.session_state.global_results_pool = []
            st.session_state.submitted = False
            st.rerun()
        
        tab1, tab2 = st.tabs(["📝 Logs", "➕ Questions"])
        with tab1:
            st.subheader("🔒 Terminal Records")
            st.table(get_results_from_sheet())

    # Student Panel
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Terminal")
        st.write(f"User: {st.session_state.username}")
        # Examination logic here...
