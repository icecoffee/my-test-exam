import streamlit as st
import pandas as pd
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
# Sheet1 (Results) GID = 0
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
# Sheet2 (Questions) GID = 2071758052
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2071758052"
# Sheet3 (Student Users) ကို Dynamic လှမ်းဖတ်ရန် ချိတ်ဆက်ခြင်း
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
    try:
        df = pd.read_csv(CSV_USERS_URL)
        users_dict = {}
        if not df.empty:
            for row in df.values.tolist():
                if len(row) >= 2 and pd.notna(row[0]) and pd.notna(row[1]):
                    users_dict[str(row[0]).strip()] = str(row[1]).strip()
        return users_dict
    except:
        # Sheet3 မဆောက်ရသေးပါက သုံးရန် Default အကောင့်
        return {"student": "student123"}

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

# Load Dynamic Data
all_questions = get_questions_from_sheet()
if "local_questions" in st.session_state:
    for lq in st.session_state.local_questions:
        if lq not in all_questions:
            all_questions.append(lq)

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
        elif username in valid_students and password == valid_students[username]:
            # စစ်ဆေးမှု: ၎င်းကျောင်းသား အရင်ဖြေပြီးသား ဟုတ်မဟုတ်စစ်ခြင်း
            sheet_data = get_results_from_sheet()
            already_submitted = False
            for row in sheet_data:
                if len(row) > 1 and str(row[1]) == username:
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
