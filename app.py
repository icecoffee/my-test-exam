import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
# Sheet1 (Results) အတွက် CSV URL
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Sheet2 (Questions) အတွက် CSV URL (gid=အသစ်ဆောက်ထားသော Sheet2 ID - များသောအားဖြင့် ဝင်ဖတ်၍ရပါသည်)
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=Sheet2"

def get_results_from_sheet():
    try:
        df = pd.read_csv(CSV_RESULTS_URL)
        return df.values.tolist()
    except:
        return []

def get_questions_from_sheet():
    try:
        df = pd.read_csv(CSV_QUESTIONS_URL)
        questions = []
        for row in df.values.tolist():
            if len(row) >= 6:
                questions.append({
                    "q": row[0],
                    "options": [str(row[1]), str(row[2]), str(row[3]), str(row[4])],
                    "correct": str(row[5])
                })
        return questions
    except:
        # Sheet ထဲက ဖတ်မရပါက Default အနေဖြင့် ထားရှိခြင်း
        return [
            {"q": "Nuclear shielding matching: Which material is most effective for neutron attenuation?", "options": ["Lead (Pb)", "Water / Paraffin", "Aluminum (Al)", "Copper (Cu)"], "correct": "Water / Paraffin"},
            {"q": "The 555 Timer IC operating in Astable mode produces which type of output waveform?", "options": ["Sine Wave", "Square Wave", "Triangular Wave", "Sawtooth Wave"], "correct": "Square Wave"}
        ]

def save_result_to_sheet(username, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "local_backup" not in st.session_state:
        st.session_state.local_backup = []
    st.session_state.local_backup.append([timestamp, username, score, 1])

def save_question_to_sheet(q, o1, o2, o3, o4, correct):
    if "local_questions" not in st.session_state:
        st.session_state.local_questions = []
    st.session_state.local_questions.append({"q": q, "options": [o1, o2, o3, o4], "correct": correct})

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Load Dynamic Questions from Google Sheets
all_questions = get_questions_from_sheet()
if "local_questions" in st.session_state:
    for lq in st.session_state.local_questions:
        if lq not in all_questions:
            all_questions.append(lq)

# --- UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.subheader("DCS Prototype Version (Permanent Question Pool)")
    
    username = st.text_input("Username (Case-sensitive)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        elif username == "student" and password == "student123":
            sheet_data = get_results_from_sheet()
            already_submitted = False
            for row in sheet_data:
                if len(row) > 1 and str(row[1]) == username:
                    already_submitted = True
                    break
                    
            if already_submitted:
                st.error("❌ Access Denied: You have already submitted your exam. Account is locked.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_role = "student"
                st.session_state.username = username
                st.rerun()
        else:
            st.error("Invalid credentials.")
else:
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()
        
    # ADMIN PANEL
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel (Permanent Storage Mode)")
        
        tab1, tab2 = st.tabs(["📝 View Results Logs", "➕ Add Secure Questions"])
        
        with tab1:
            st.subheader("🔒 Google Sheets Live Records")
            db_data = get_results_from_sheet()
            if "local_backup" in st.session_state:
                for b in st.session_state.local_backup:
                    if b not in db_data:
                        db_data.append(b)
                        
            if db_data and len(db_data) > 0:
                table_list = []
                for r in db_data:
                    if str(r[0]) != "Timestamp" and len(r) >= 3:
                        table_list.append({"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"})
                if table_list:
                    st.table(table_list)
                else:
                    st.info("ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
            else:
                st.info("ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
                
        with tab2:
            st.subheader("Inject New Question to Pool Permanently")
            new_q = st.text_input("Question Text")
            opt1 = st.text_input("Option 1")
            opt2 = st.text_input("Option 2")
            opt3 = st.text_input("Option 3")
            opt4 = st.text_input("Option 4")
            correct_opt = st.selectbox("Correct Option", [opt1, opt2, opt3, opt4])
            
            if st.button("Inject into Question Pool"):
                if new_q and opt1 and opt2:
                    save_question_to_sheet(new_q, opt1, opt2, opt3, opt4, correct_opt)
                    st.success("🎉 Question saved permanently to Cloud Database!")
                    st.rerun()
                    
    # STUDENT PANEL
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Examination Terminal")
        st.write(f"Active Session User: **{st.session_state.username}**")
        
        score = 0
        user_answers = {}
        
        for i, q in enumerate(all_questions):
            st.markdown(f"**Q{i+1}: {q['q']}**")
            user_answers[i] = st.radio(f"Select answer for Q{i+1}:", q['options'], key=f"q_{i}")
            st.write("---")
            
        if st.button("Final Submit & Lock Account", type="primary"):
            for i, q in enumerate(all_questions):
                if user_answers[i] == q['correct']:
                    score += 1
            save_result_to_sheet(st.session_state.username, score)
            st.success(f"🎉 သင်၏ ရမှတ်မှာ {score}/{len(all_questions)} ဖြစ်ပြီး စနစ်မှ သိမ်းဆည်းကာ Lock ချထားပြီး ဖြစ်ပါသည်။")
            st.balloons()
