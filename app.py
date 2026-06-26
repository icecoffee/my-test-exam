import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.request
import json

# --- CONFIG & URLS ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwyFMXmqgLQyIx-kUN54Q5oVV4q8T1WJEvoksyo_EugBLAYeZ9SUQt35BpQF8pWMOmbcQ/exec"

def get_questions_from_sheet():
    try:
        df = pd.read_csv(CSV_QUESTIONS_URL)
        questions = []
        for _, row in df.iterrows():
            questions.append({"q": str(row[0]), "options": [str(row[1]), str(row[2]), str(row[3]), str(row[4])], "correct": str(row[5])})
        return questions
    except: return []

# --- MAIN APP ---
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
        tab1, tab2 = st.tabs(["📝 View Results", "➕ Add Questions"])
        
        with tab1:
            st.table(pd.read_csv(CSV_RESULTS_URL))
            
        with tab2:
            st.info("💡 မေးခွန်းအသစ်များအတွက် Google Sheet (Sheet2) ကိုဖွင့်ပြီး အောက်ပါအတိုင်း ဖြည့်စွက်ပါ:")
            st.write("Column A: မေးခွန်း | B, C, D, E: အဖြေရွေးချယ်စရာများ | F: အဖြေမှန်")
            st.link_button("Go to Google Sheet", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

    # --- STUDENT PANEL ---
    else:
        st.title("✍️ Student Examination Terminal")
        questions = get_questions_from_sheet()
        if questions:
            user_answers = {}
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q['q']}**")
                user_answers[i] = st.radio(f"Select Q{i+1}", q['options'], index=None, key=f"q{i}")
            
            if st.button("Submit Exam"):
                score = sum(1 for i, q in enumerate(questions) if user_answers.get(i) == q['correct'])
                st.success(f"🎉 သင်၏ ရမှတ်မှာ {score}/{len(questions)} ဖြစ်ပါသည်။")
        else:
            st.warning("⚠️ မေးခွန်းများ မတွေ့ရှိပါ။ Sheet2 တွင် ဒေတာရှိမရှိ စစ်ဆေးပါ။")
