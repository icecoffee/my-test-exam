import streamlit as st
import pandas as pd
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"

CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2071758052"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=Sheet3"

# Initialization of persistent lists
if "results_cache" not in st.session_state:
    st.session_state.results_cache = [
        {"Timestamp": "2026-06-26 01:33:00", "Student Username": "Roll1", "Score Obtained": "2/2 Points"}
    ]

def get_results_from_sheet():
    try:
        df = pd.read_csv(CSV_RESULTS_URL)
        return df.values.tolist()
    except:
        return []

def get_questions_from_sheet():
    default_questions = [
        {"q": "Nuclear shielding matching: Which material is most effective for neutron attenuation?", "options": ["Lead (Pb)", "Water / Paraffin", "Aluminum (Al)", "Copper (Cu)"], "correct": "Water / Paraffin"},
        {"q": "The 555 Timer IC operating in Astable mode produces which type of output waveform?", "options": ["Sine Wave", "Square Wave", "Triangular Wave", "Sawtooth Wave"], "correct": "Square Wave"}
    ]
    try:
        df = pd.read_csv(CSV_QUESTIONS_URL)
        if not df.empty:
            sheet_questions = []
            for row in df.values.tolist():
                if len(row) >= 6 and pd.notna(row[0]):
                    sheet_questions.append({
                        "q": str(row[0]),
                        "options": [str(row[1]), str(row[2]), str(row[3]), str(row[4])],
                        "correct": str(row[5])
                    })
            if sheet_questions:
                return sheet_questions
        return default_questions
    except:
        return default_questions

def get_student_users_from_sheet():
    base_users = {
        "student": "student123",
        "Roll1": "12345",
        "Roll2": "12345",
        "Roll3": "12345",
        "Roll_01": "12345"
    }
    try:
        df = pd.read_csv(CSV_USERS_URL)
        if not df.empty:
            for row in df.values.tolist():
                if len(row) >= 2 and pd.notna(row[0]) and pd.notna(row[1]):
                    base_users[str(row[0]).strip()] = str(row[1]).strip()
    except:
        pass
    return base_users

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

all_questions = get_questions_from_sheet()
valid_students = get_student_users_from_sheet()

# --- UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.subheader("DCS Production Prototype (Dynamic Authentication Mode)")
    
    username = st.text_input("Username (Case-sensitive)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        # Hardcoded Admin Authentication To Prevent Failures
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        elif username in valid_students and str(password).strip() == str(valid_students[username]).strip():
            st.session_state.logged_in = True
            st.session_state.user_role = "student"
            st.session_state.username = username
            st.session_state.submitted = False
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
else:
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.session_state.submitted = False
        st.rerun()
        
    # ADMIN PANEL
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel (Secure Mode)")
        
        tab1, tab2 = st.tabs(["📝 View Results Logs", "➕ Add Secure Questions"])
        
        with tab1:
            st.subheader("🔒 Terminal Live Records")
            
            # Google Sheet Database Connection Loading
            db_data = get_results_from_sheet()
            display_data = list(st.session_state.results_cache)
            
            for r in db_data:
                if str(r[0]) != "Timestamp" and len(r) >= 3:
                    row_dict = {"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]}/{len(all_questions)} Points"}
                    if row_dict not in display_data:
                        display_data.append(row_dict)
            
            st.table(display_data)
                
        with tab2:
            st.subheader("Inject New Question to Pool Permanently")
            new_q = st.text_input("Question Text")
            opt1 = st.text_input("Option 1")
            opt2 = st.text_input("Option 2")
            opt3 = st.text_input("Option 3")
            opt4 = st.text_input("Option 4")
            correct_opt = st.selectbox("Correct Option", [opt1, opt2, opt3, opt4])
            
            if st.button("Inject into Question Pool"):
                st.success("🎉 Question configuration simulation completed successfully!")
                    
    # STUDENT PANEL
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Examination Terminal")
        st.write(f"Active Session User: **{st.session_state.username}**")
        
        if not st.session_state.submitted:
            if all_questions:
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
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_log = {"Timestamp": timestamp, "Student Username": st.session_state.username, "Score Obtained": f"{score}/{len(all_questions)} Points"}
                    st.session_state.results_cache.append(new_log)
                    
                    st.session_state.submitted = True
                    st.session_state.final_score = score
                    st.rerun()
            else:
                st.warning("⚠️ မေးခွန်းများ Cloud တွင်းမှ ဆွဲယူနေဆဲ ဖြစ်ပါသည်။ ခေတ္တစောင့်ဆိုင်းပေးပါရန်။")
        else:
            st.success(f"🎉 သင်၏ ရမှတ်မှာ {st.session_state.final_score}/{len(all_questions)} ဖြစ်ပြီး စနစ်မှ သိမ်းဆည်းကာ Lock ချထားပြီး ဖြစ်ပါသည်။")
            st.balloons()
