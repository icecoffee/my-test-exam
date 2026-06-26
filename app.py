import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.request
import json

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"

CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"

# ဆရာ့ရဲ့ Apps Script Web App URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzIGCo5gvafmu4M2B9FEwEOichPdCDOLFmtmcsz9YaM0GzrG-DDe2u4HYVt3D66xeE9fg/exec"

# --- GLOBAL LIVE MEMORY POOL FOR ADMIN VIEW ---
if "global_results_pool" not in st.session_state:
    st.session_state.global_results_pool = []

def get_results_from_sheet():
    try:
        df = pd.read_csv(CSV_RESULTS_URL)
        return df.values.tolist()
    except:
        return []

def get_questions_from_sheet():
    try:
        df = pd.read_csv(CSV_QUESTIONS_URL)
        if df is not None and not df.empty:
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
    except:
        pass
        
    return [
        {"q": "Nuclear shielding matching: Which material is most effective for neutron attenuation?", "options": ["Lead (Pb)", "Water / Paraffin", "Aluminum (Al)", "Copper (Cu)"], "correct": "Water / Paraffin"},
        {"q": "The 555 Timer IC operating in Astable mode produces which type of output waveform?", "options": ["Sine Wave", "Square Wave", "Triangular Wave", "Sawtooth Wave"], "correct": "Square Wave"}
    ]

def get_student_users_from_sheet():
    base_users = {
        "student": "student123",
        "Roll1": "12345",
        "Roll2": "12345"
    }
    try:
        df = pd.read_csv(CSV_USERS_URL)
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip()
            user_col = [c for c in df.columns if 'user' in c.lower()][0]
            pwd_col = [c for c in df.columns if 'pass' in c.lower()][0]
            
            for _, row in df.iterrows():
                if pd.notna(row[user_col]) and pd.notna(row[pwd_col]):
                    base_users[str(row[user_col]).strip()] = str(row[pwd_col]).strip()
    except:
        pass
    return base_users

def save_result_to_sheet(username, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = [timestamp, username, score]
    if new_record not in st.session_state.global_results_pool:
        st.session_state.global_results_pool.append(new_record)
        
    try:
        payload = json.dumps({"timestamp": timestamp, "username": username, "score": int(score)}).encode('utf-8')
        req = urllib.request.Request(WEB_APP_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Secure Exam Terminal", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "username" not in st.session_state: st.session_state.username = None
if "submitted" not in st.session_state: st.session_state.submitted = False

# --- UI LOGIC ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Online Examination System")
    st.subheader("DCS Production Prototype (Dynamic Authentication Mode)")
    
    username = st.text_input("Username (Case-sensitive)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        # 💡 [ပြင်ဆင်ချက်] - Admin ကို Sheet ဒေတာများ မဖတ်မီ အပေါ်ဆုံးကနေ လုံးဝ သီးသန့် အရင်စစ်ထုတ်ပြီး ချက်ချင်းပေးဝင်လိုက်ပါသည်
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        else:
            # ကျောင်းသားဖြစ်မှသာ Sheet ထဲက ဒေတာများကို လှမ်းယူစစ်ဆေးပါမည်
            valid_students = get_student_users_from_sheet()
            if username in valid_students and str(password).strip() == str(valid_students[username]).strip():
                sheet_data = get_results_from_sheet()
                already_submitted = False
                
                for row in sheet_data:
                    if len(row) > 1 and str(row[1]) == username:
                        already_submitted = True
                        break
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
            st.subheader("🔒 Terminal Live Records")
            db_data = get_results_from_sheet()
            display_data = []
            
            for r in db_data:
                if len(r) >= 3 and str(r[0]).lower() != "timestamp":
                    display_data.append({"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"})
            
            for r in st.session_state.global_results_pool:
                row_dict = {"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"}
                if row_dict not in display_data:
                    display_data.append(row_dict)
            
            if display_data:
                st.table(display_data)
            else:
                st.info("ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
                
        with tab2:
            st.subheader("Inject New Question to Pool Permanently")
            st.info("💡 ဤနေရာတွင် မေးခွန်းအသစ်များကို Google Sheet (Sheet2) ထဲသို့ တိုက်ရိုက်သွားရောက်တိုးပေးရပါမည်။")
                    
    # --- STUDENT PANEL ---
    elif st.session_state.user_role == "student":
        st.title("✍️ Student Examination Terminal")
        st.write(f"Active Session User: **{st.session_state.username}**")
        
        all_questions = get_questions_from_sheet()
        
        if not st.session_state.submitted:
            if all_questions:
                score = 0
                user_answers = {}
                
                for i, q in enumerate(all_questions):
                    st.markdown(f"##### Q{i+1}: {q['q']}")
                    user_answers[i] = st.radio(f"Select answer for Q{i+1}:", q['options'], key=f"q_{i}")
                    st.write("---")
                    
                if st.button("Final Submit & Lock Account", type="primary"):
                    for i, q in enumerate(all_questions):
                        if user_answers[i] == q['correct']:
                            score += 1
                    
                    save_result_to_sheet(st.session_state.username, score)
                    st.session_state.submitted = True
                    st.session_state.final_score = score
                    st.rerun()
            else:
                st.warning("⚠️ မေးခွန်းများ Cloud တွင်းမှ ဆွဲယူနေဆဲ ဖြစ်ပါသည်။ ခေတ္တစောင့်ဆိုင်းပေးပါရန်။")
        else:
            disp_score = st.session_state.final_score if 'final_score' in st.session_state else 0
            st.success(f"🎉 သင်၏ ရမှတ်မှာ {disp_score}/{len(all_questions)} ဖြစ်ပြီး စနစ်မှ သိမ်းဆည်းကာ Lock ချထားပြီး ဖြစ်ပါသည်။")
            st.balloons()
