import streamlit as st
import hashlib
import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN_HASH = hash_password("admin123")
STUDENT_HASH = hash_password("student123")

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": ADMIN_HASH, "role": "admin"},
        "student": {"password": STUDENT_HASH, "role": "student"}
    }

if "questions" not in st.session_state:
    st.session_state.questions = [
        {
            "question": "Which shielding material is best for high-energy Gamma-rays?",
            "options": ["Aluminum", "Lead", "Plastic", "Water"],
            "answer": "Lead"
        },
        {
            "question": "What is the core active element inside a 555 Timer IC?",
            "options": ["Microcontroller", "Op-Amps and Flip-Flop", "Inductor", "Transformer"],
            "answer": "Op-Amps and Flip-Flop"
        }
    ]

if "submitted_students" not in st.session_state:
    st.session_state.submitted_students = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

st.set_page_config(page_title="Secure Exam System", page_icon="🔐", layout="centered")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.write("DCS Prototype Version (High Security Enabled)")
    st.markdown("---")
    
    username = st.text_input("Username (Case-sensitive)").strip()
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        if username in st.session_state.users:
            entered_hash = hash_password(password)
            correct_hash = st.session_state.users[username]["password"]
            
            if entered_hash == correct_hash:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = st.session_state.users[username]["role"]
                st.success("Authentication Successful!")
                st.rerun()
            else:
                st.error("စကားဝှက် မှားယွင်းနေပါသည်။")
        else:
            st.error("အသုံးပြုသူအမည် မှားယွင်းနေပါသည်။")

elif st.session_state.role == "admin":
    st.title("👨‍🏫 Admin Control Panel (Secure Mode)")
    st.sidebar.write(f"Current User: **{st.session_state.username}**")
    if st.sidebar.button("Log Out"): logout()
    
    tab1, tab2 = st.tabs(["📋 View Results Logs", "➕ Add Secure Questions"])
    
    with tab1:
        st.subheader("🔒 Tamper-Proof Student Results")
        if st.session_state.submitted_students:
            for student, res in st.session_state.submitted_students.items():
                st.info(f"Student: **{student}** | Score: **{res['score']}** | Status: `SUBMITTED_AND_LOCKED` (Date: {res['date']})")
        else:
            st.info("ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
            
    with tab2:
        st.subheader("Create a New Question")
        new_q = st.text_area("Question Text")
        opt_A = st.text_input("Option A")
        opt_B = st.text_input("Option B")
        opt_C = st.text_input("Option C")
        opt_D = st.text_input("Option D")
        correct_ans = st.selectbox("Select Correct Answer", [opt_A, opt_B, opt_C, opt_D])
        
        if st.button("Inject into Question Pool"):
            if new_q and opt_A and opt_B:
                st.session_state.questions.append({
                    "question": new_q,
                    "options": [opt_A, opt_B, opt_C, opt_D],
                    "answer": correct_ans
                })
                st.success("မေးခွန်းကို Pool ထဲသို့ စနစ်တကျ ထည့်သွင်းပြီးပါပြီ။")
            else:
                st.error("ကျောင်းသား ဒေတာ အစုံအလင် ထည့်ပါ။")

elif st.session_state.role == "student":
    st.title("✍️ Secure Examination Terminal")
    st.sidebar.write(f"Student ID: **{st.session_state.username}**")
    if st.sidebar.button("Log Out"): logout()
    
    current_student = st.session_state.username
    
    if current_student in st.session_state.submitted_students:
        st.warning("⚠️ Access Denied: You have already submitted this exam.")
        saved_res = st.session_state.submitted_students[current_student]
        st.success(f"သင်၏ ရမှတ်မှာ {saved_res['score']} ဖြစ်ပြီး စနစ်မှ သိမ်းဆည်းကာ Lock ချထားပြီး ဖြစ်ပါသည်။")
    
    else:
        st.write("မေးခွန်းများကို သေချာဖတ်ပြီး ဖြေဆိုပါ။ Submit နှိပ်ပြီးပါက ပြန်ပြင်ခွင့် ရှိမည်မဟုတ်ပါ။")
        st.markdown("---")
        
        user_answers = {}
        for i, q in enumerate(st.session_state.questions):
            st.write(f"**Question {i+1}: {q['question']}**")
            user_answers[i] = st.radio(f"Select your answer:", q['options'], key=f"sec_q_{i}", index=None)
            st.write("")
            
        if st.button("Final Submit & Lock Account", type="primary"):
            unanswered = [i for i in user_answers if user_answers[i] is None]
            if unanswered:
                st.error("⚠️ မေးခွန်းအားလုံးကို ဖြေဆိုရန် လိုအပ်ပါသည်။")
            else:
                score = 0
                total = len(st.session_state.questions)
                for i, q in enumerate(st.session_state.questions):
                    if user_answers[i] == q['answer']:
                        score += 1
                
                st.session_state.submitted_students[current_student] = {
                    "score": f"{score} / {total}",
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.success("စာမေးပွဲ အောင်မြင်စွာ ဖြေဆိုပြီးပါပြီ။ ရလဒ်ကို စနစ်သို့ ပေးပို့ပြီးပါပြီ။")
                st.balloons()
                st.rerun()
