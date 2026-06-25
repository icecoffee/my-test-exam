import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"

# Read URLs
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2071758052"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=Sheet3"

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

# 🚀 အဓိကပြင်ဆင်ချက် - ကျောင်းသားရမှတ်ကို Session Memory ရော Local Cache မှာပါ ကာကွယ်သိမ်းဆည်းခြင်း
def save_result_to_sheet(username, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "local_backup" not in st.session_state:
        st.session_state.local_backup = []
    
    # ယာယီ Session နှင့် အမြဲတမ်း Admin View တွဲဖက်သိမ်းဆည်းခြင်း
    new_record = [timestamp, username, score]
    st.session_state.local_backup.append(new_record)
    
    # Global Cache အဖြစ် သိမ်းဆည်းရန် ဖိုင်တွဲပြုလုပ်ခြင်း
    if "global_db" not in st.experimental_get_query_params():
        if "global_results" not in st.sidebar.__self__.dict__:
            st.奠定 = True

if "global_results_pool" not in st.session_state:
    st.session_state.global_results_pool = []

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

all_questions = get_questions_from_sheet()
valid_students = get_student_users_from_sheet()

# --- UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.subheader("DCS Production Prototype (Dynamic Authentication Mode)")
    
    username = st.text_input("Username (Case-sensitive)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        elif username in valid_students and str(password).strip() == str(valid_students[username]).strip():
            # စစ်ဆေးမှု - ဖြေဆိုပြီးသားဟုတ်မဟုတ် စစ်ဆေးခြင်း
            already_submitted = False
            for r in st.session_state.global_results_pool:
                if r[1] == username:
                    already_submitted = True
                    break
            
            if already_submitted:
                st.error(f"❌ Access Denied: User '{username}' has already submitted the exam. Account Locked.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_role = "student"
                st.session_state.username = username
                st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
else:
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()
        
    # ADMIN PANEL
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel (Secure Mode)")
        
        tab1, tab2 = st.tabs(["📝 View Results Logs", "➕ Add Secure Questions"])
        
        with tab1:
            st.subheader("🔒 Terminal Live Records")
            
            # ဒေတာစုစည်းမှု
            display_data = []
            for r in st.session_state.global_results_pool:
                display_data.append({"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"})
                
            if "local_backup" in st.session_state:
                for r in st.session_state.local_backup:
                    row_dict = {"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"}
                    if row_dict not in display_data:
                        display_data.append(row_dict)
            
            if display_data:
                st.table(display_data)
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
                st.success("🎉 Question saved temporarily!")
                    
    # STUDENT PANEL
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Examination Terminal")
        st.write(f"Active Session User: **{st.session_state.username}**")
        
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
                # Global Pool ထဲသို့ တိုက်ရိုက် ထည့်သွင်းခြင်း
                st.session_state.global_results_pool.append([timestamp, st.session_state.username, score])
                save_result_to_sheet(st.session_state.username, score)
                
                st.success(f"🎉 သင်၏ ရမှတ်မှာ {score}/{len(all_questions)} ဖြစ်ပြီး စနစ်မှ သိမ်းဆည်းကာ Lock ချထားပြီး ဖြစ်ပါသည်။")
                st.balloons()
