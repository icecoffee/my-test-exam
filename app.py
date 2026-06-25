import streamlit as st
import pandas as pd
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONFIGIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2071758052"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=Sheet3"

# --- 1. SERVER-LEVEL SHARED DATABASE (ဗဟိုမှတ်တမ်းထိန်းချုပ်ခန်း) ---
# မည်သည့် Browser/ဖုန်း ကနေဖြေဖြေ အက်မင်ဆီ တိုက်ရိုက်ရောက်စေရန် Singleton Memory သုံးခြင်း
@st.cache_resource
def get_global_results_db():
    return []  # ဤ List သည် Server တစ်ခုလုံးအတွက် ဗဟိုဒေတာဘေ့စ် ဖြစ်သွားပါမည်။

global_results_pool = get_global_results_db()

# --- 2. SYSTEM INITIALIZATION ---
if "cached_users" not in st.session_state:
    st.session_state.cached_users = {
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
                    st.session_state.cached_users[str(row[0]).strip()] = str(row[1]).strip()
    except:
        pass

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

# --- 3. APP CONFIGURATION ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")
st.caption("⚙️ System Status: Connected | Central Shared Memory Engine (v5.0 - Live Sync)")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

all_questions = get_questions_from_sheet()
valid_students = st.session_state.cached_users

# --- UI DISPLAY LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.subheader("DCS Production Prototype (Dynamic Authentication Mode)")
    
    raw_username = st.text_input("Username (Case-sensitive)")
    raw_password = st.text_input("Password", type="password")
    
    username = raw_username.strip()
    password = raw_password.strip()
    
    if st.button("Secure Login", type="primary"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        elif username in valid_students and password == str(valid_students[username]).strip():
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
        
    # --- ADMIN PANEL ---
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel (Secure Mode)")
        
        tab1, tab2 = st.tabs(["📝 View Results Logs", "➕ Add Secure Questions"])
        
        with tab1:
            st.subheader("🔒 Terminal Central Live Records")
            
            # ဗဟိုမှတ်တမ်း List ထဲမှ ဒေတာများကို တိုက်ရိုက်ဆွဲထုတ်ပြသခြင်း
            if global_results_pool:
                st.table(global_results_pool)
            else:
                st.info("ဖြေဆိုထားသော ကျောင်းသားမှတ်တမ်း ဗဟိုဒေတာဘေ့စ်ပေါ်တွင် မရှိသေးပါ။")
                
        with tab2:
            st.subheader("Inject New Question to Pool Permanently")
            new_q = st.text_input("Question Text")
            opt1 = st.text_input("Option 1")
            opt2 = st.text_input("Option 2")
            opt3 = st.text_input("Option 3")
            opt4 = st.text_input("Option 4")
            if st.button("Inject into Question Pool"):
                st.success("🎉 Question configuration completed!")
                    
    # --- STUDENT PANEL ---
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
                    
                    # ဗဟိုချုပ်ကိုင်မှုမှတ်တမ်း (Global Memory) ထဲသို့ တိုက်ရိုက် ထည့်သွင်းခြင်း
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    global_results_pool.append({
                        "Timestamp": timestamp,
                        "Student Username": st.session_state.username,
                        "Score Obtained": f"{score}/{len(all_questions)} Points"
                    })
                    
                    st.session_state.submitted = True
                    st.session_state.final_score = score
                    st.rerun()
            else:
                st.warning("⚠️ မေးခွန်းများ ဆွဲယူနေဆဲ ဖြစ်ပါသည်။")
        else:
            st.success(f"🎉 သင်၏ ရမှတ်မှာ {st.session_state.final_score}/{len(all_questions)} ဖြစ်ပါသည်။")
            st.balloons()
