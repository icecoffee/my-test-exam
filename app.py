import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Google Sheet ID နှင့် လင့်ခ်များ
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"

# Google Form Submission URL (ဆရာ့ Google Form ရဲ့ Response URL)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSclK7tUfS_R52OaOunA-bE_P7m84_j9iU5RstWb7pAic9_U4A/formResponse"

# --- LOGIN & STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

# --- ADMIN PANEL (Google Sheet မှ ဖတ်ရန်) ---
def show_admin():
    st.title("👩‍🏫 Admin Control Panel")
    if st.button("Refresh Records"): st.rerun()
    try:
        # Sheet1 မှ အဖြေများကို ဖတ်ခြင်း
        df = pd.read_csv(CSV_RESULTS_URL)
        st.table(df)
    except:
        st.write("Record များ တင်ဆောင်နေသည်...")

# --- STUDENT PANEL (Google Form သို့ ပို့ရန်) ---
def show_student():
    st.title("✍️ Exam Terminal")
    username = st.session_state.username
    st.write(f"User: {username}")
    
    # ဤနေရာတွင် မေးခွန်းများကို Google Form ပုံစံဖြင့် တိုက်ရိုက်ချိတ်ဆက်ဖြေဆိုခိုင်းပါ
    st.markdown(f"[ဖြေဆိုရန် ဤနေရာကိုနှိပ်ပါ](https://docs.google.com/forms/d/e/1FAIpQLSclK7tUfS_R52OaOunA-bE_P7m84_j9iU5RstWb7pAic9_U4A/viewform?usp=pp_url&entry.12345={username})")

# --- MAIN LOGIC ---
if not st.session_state.logged_in:
    user = st.text_input("Username")
    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.username = user
        st.rerun()
else:
    if st.session_state.username == "admin": show_admin()
    else: show_student()
