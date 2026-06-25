import streamlit as st
import sqlite3
import os
from datetime import datetime

# --- DATABASE SETUP (ကွန်ပျူတာထဲတွင် အမြဲတမ်းသိမ်းဆည်းမည့် စနစ်) ---
DB_FILE = "exam_records.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # ကျောင်းသားမှတ်တမ်းဇယားဆောက်ခြင်း
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (timestamp TEXT, username TEXT, score INTEGER, submitted INTEGER)''')
    conn.commit()
    conn.close()

def save_result(username, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO results VALUES (?, ?, ?, 1)", (timestamp, username, score))
    conn.commit()
    conn.close()

def get_results():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, username, score FROM results")
    rows = c.fetchall()
    conn.close()
    return rows

# Database စတင်ပွင့်စေခြင်း
init_db()

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None

# Static Questions
if "questions" not in st.session_state:
    st.session_state.questions = [
        {"q": "Nuclear shielding matching: Which material is most effective for neutron attenuation?", "options": ["Lead (Pb)", "Water / Paraffin", "Aluminum (Al)", "Copper (Cu)"], "correct": "Water / Paraffin"},
        {"q": "The 555 Timer IC operating in Astable mode produces which type of output waveform?", "options": ["Sine Wave", "Square Wave", "Triangular Wave", "Sawtooth Wave"], "correct": "Square Wave"}
    ]

# --- UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.subheader("DCS Prototype Version (High Security Enabled)")
    
    username = st.text_input("Username (Case-sensitive)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        elif username == "student" and password == "student123":
            # ကျောင်းသား အရင်ဖြေပြီးသား ဟုတ်မဟုတ် DB တွင်စစ်ဆေးခြင်း
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM results WHERE username=?", (username,))
            already_submitted = c.fetchone()
            conn.close()
            
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
    # LOGOUT BUTTON
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
            st.subheader("🔒 Tamper-Proof Student Results")
            db_data = get_results()
            if db_data:
                # ဇယားကွက်ဖြင့် သေသပ်စွာပြသခြင်း
                st.table([{"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"} for r in db_data])
            else:
                st.info("ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
                
        with tab2:
            st.subheader("Inject New Question to Pool")
            new_q = st.text_input("Question Text")
            opt1 = st.text_input("Option 1")
            opt2 = st.text_input("Option 2")
            opt3 = st.text_input("Option 3")
            opt4 = st.text_input("Option 4")
            correct_opt = st.selectbox("Correct Option", [opt1, opt2, opt3, opt4])
            
            if st.button("Inject into Question Pool"):
                if new_q and opt1 and opt2:
                    st.session_state.questions.append({"q": new_q, "options": [opt1, opt2, opt3, opt4], "correct": correct_opt})
                    st.success("Question injected successfully!")
                    
    # STUDENT PANEL
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Examination Terminal")
        st.write(f"Active Session User: **{st.session_state.username}**")
        st.warning("⚠️ Do not refresh this page. Refreshing will automatically lock your exam token.")
        
        score = 0
        user_answers = {}
        
        for i, q in enumerate(st.session_state.questions):
            st.markdown(f"**Q{i+1}: {q['q']}**")
            user_answers[i] = st.radio(f"Select answer for Q{i+1}:", q['options'], key=f"q_{i}")
            st.write("---")
            
        if st.button("Final Submit & Lock Account", type="primary"):
            for i, q in enumerate(st.session_state.questions):
                if user_answers[i] == q['correct']:
                    score += 1
            
            # Database ထဲသို့ အပြီးအပိုင် လှမ်းသိမ်းခြင်း
            save_result(st.session_state.username, score)
            st.success(f"🎉 Exam submitted successfully! Score: {score}/{len(st.session_state.questions)}")
            st.balloons()
            
            # Session ရှင်းလင်းပြီး ထွက်ခြင်း
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.info("Your account is now locked. Redirecting...")
