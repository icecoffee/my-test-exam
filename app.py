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
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwyFMXmqgLQyIx-kUN54Q5oVV4q8T1WJEvoksyo_EugBLAYeZ9SUQt35BpQF8pWMOmbcQ/exec"

def get_mm_now(): return datetime.utcnow() + timedelta(hours=6, minutes=30)

if "global_results_pool" not in st.session_state: st.session_state.global_results_pool = []

def get_questions_from_sheet():
    try:
        df = pd.read_csv(CSV_QUESTIONS_URL)
        questions = []
        for _, row in df.iterrows():
            questions.append({"q": row[0], "options": [row[1], row[2], row[3], row[4]], "correct": row[5]})
        return questions
    except: return []

def save_result_to_sheet(username, score):
    payload = json.dumps({"timestamp": get_mm_now().strftime("%Y-%m-%d %H:%M:%S"), "username": username, "score": score}).encode('utf-8')
    req = urllib.request.Request(WEB_APP_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req, timeout=3)

# --- APP START ---
st.set_page_config(page_title="Secure Exam Terminal", layout="wide")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Secure Login"):
        st.session_state.logged_in = True
        st.session_state.user_role = "admin" if username == "admin" else "student"
        st.session_state.username = username
        st.rerun()
else:
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ADMIN PANEL ---
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel")
        st.sidebar.subheader("⚙️ System Control")
        if st.sidebar.button("♻️ FULL SYSTEM RESET"):
            st.session_state.global_results_pool = []
            st.rerun()
        
        with st.tabs(["📝 View Results", "➕ Add Questions"])[0]:
            st.table(pd.read_csv(CSV_RESULTS_URL))

    # --- STUDENT PANEL ---
    else:
        st.title("✍️ Student Terminal")
        st.write(f"User: **{st.session_state.username}**")
        questions = get_questions_from_sheet()
        
        if questions:
            user_answers = {}
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q['q']}**")
                user_answers[i] = st.radio(f"Select Q{i+1}", q['options'], index=None, key=f"q{i}")
            
            if st.button("Submit"):
                score = sum(1 for i, q in enumerate(questions) if user_answers.get(i) == q['correct'])
                save_result_to_sheet(st.session_state.username, score)
                st.success(f"Score: {score}/{len(questions)}")
        else:
            st.warning("Loading questions...")
