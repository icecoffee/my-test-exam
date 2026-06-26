import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.request
import json
import time

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwyFMXmqgLQyIx-kUN54Q5oVV4q8T1WJEvoksyo_EugBLAYeZ9SUQt35BpQF8pWMOmbcQ/exec"

EXAM_DURATION_MINUTES = 5

if "global_results_pool" not in st.session_state:
    st.session_state.global_results_pool = []

def get_results_from_sheet():
    try: return pd.read_csv(CSV_RESULTS_URL).values.tolist()
    except: return []

def get_questions_from_sheet():
    try:
        df = pd.read_csv(CSV_QUESTIONS_URL)
        sheet_questions = []
        for row in df.values.tolist():
            if len(row) >= 6 and pd.notna(row[0]):
                sheet_questions.append({"q": str(row[0]), "options": [str(row[1]), str(row[2]), str(row[3]), str(row[4])], "correct": str(row[5])})
        return sheet_questions if sheet_questions else []
    except: return []

def get_student_users_from_sheet():
    base_users = {"student": "student123", "Roll1": "12345", "Roll2": "12345"}
    try:
        df = pd.read_csv(CSV_USERS_URL)
        df.columns = df.columns.str.strip()
        user_col, pwd_col = [c for c in df.columns if 'user' in c.lower()][0], [c for c in df.columns if 'pass' in c.lower()][0]
        for _, row in df.iterrows():
            if pd.notna(row[user_col]): base_users[str(row[user_col]).strip()] = str(row[pwd_col]).strip()
    except: pass
    return base_users

def save_result_to_sheet(username, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.global_results_pool.append([timestamp, username, score])
    try:
        payload = json.dumps({"timestamp": timestamp, "username": username, "score": int(score)}).encode('utf-8')
        req = urllib.request.Request(WEB_APP_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=3)
    except: pass

st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Secure Login"):
        users = get_student_users_from_sheet()
        if username == "admin" and password == "admin123":
            st.session_state.update(logged_in=True, user_role="admin", username="admin")
            st.rerun()
        elif username in users and str(password).strip() == users[username]:
            st.session_state.update(logged_in=True, user_role="student", username=username, submitted=False, start_time=datetime.now())
            st.rerun()
else:
    if st.sidebar.button("Log Out"): st.session_state.clear(); st.rerun()
    
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Panel")
        db_data = get_results_from_sheet()
        display_data = [{"Timestamp": r[0], "User": r[1], "Score": r[2]} for r in db_data if len(r) >= 3 and str(r[0]) != "timestamp"]
        if display_data: st.table(display_data)
        else: st.info("မှတ်တမ်းမရှိသေးပါ။")
            
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Examination Terminal")
        
        # --- FIXED TIMER LOGIC ---
        if not st.session_state.submitted:
            elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
            remaining = (EXAM_DURATION_MINUTES * 60) - elapsed
            
            if remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                st.sidebar.warning(f"⏳ ကျန်ရှိချိန်: {mins:02d}:{secs:02d}")
            else: st.error("⏰ အချိန်ကုန်သွားပါပြီ!")
            
            all_q = get_questions_from_sheet()
            user_ans = {i: st.radio(q['q'], q['options'], index=None, key=f"q{i}") for i, q in enumerate(all_q)}
            
            if st.button("Final Submit"):
                score = sum(1 for i, q in enumerate(all_q) if str(user_ans[i]) == str(q['correct']))
                save_result_to_sheet(st.session_state.username, score)
                st.session_state.submitted = True
                st.rerun()
        else:
            st.success("🎉 ဖြေဆိုပြီးပါပြီ။")
