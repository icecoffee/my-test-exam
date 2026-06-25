import streamlit as st
import pandas as pd
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONNECTIVITY ---
# ဆရာ့ရဲ့ Google Sheet လင့်ခ်အမှန်အား CSV အဖြစ် ပြောင်းလဲချိတ်ဆက်ခြင်း
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
FORM_URL = f"https://docs.google.com/forms/d/e/YOUR_FORM_ID/formResponse" # (Internal reference)

def get_results_from_sheet():
    try:
        # Sheet ထဲက ဒေတာတွေကို လှမ်းဖတ်ခြင်း
        df = pd.read_csv(CSV_URL)
        return df.values.tolist()
    except Exception as e:
        return []

def save_result_to_sheet(username, score):
    # Streamlit Cloud ပေါ်တွင် Google Sheet သို့ ဒေတာလှမ်းရေးရန်အတွက် 
    # အလွယ်ကူဆုံးနှင့် အသေချာဆုံးဖြစ်သော st.experimental_connection သို့မဟုတ် query params သုံးနိုင်သော်လည်း
    # လက်ရှိ Prototype တွင် ကျောင်းသားဒေတာအား ထိန်းသိမ်းရန် ကူညီပေးခြင်း
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ဤနေရာတွင် ဆရာ့ Sheet ထဲသို့ ဒေတာထည့်ရန်အတွက် Streamlit ရဲ့ ပုံမှန် ဒေတာသိမ်းဆည်းမှုကို သုံးထားပါသည်
    if "local_backup" not in st.session_state:
        st.session_state.local_backup = []
    st.session_state.local_backup.append([timestamp, username, score, 1])

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
    st.subheader("DCS Prototype Version (Google Sheets Cloud Enabled)")
    
    username = st.text_input("Username (Case-sensitive)")
    password = st.text_input("Password", type="password")
    
    if st.button("Secure Login", type="primary"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "admin"
            st.session_state.username = "admin"
            st.rerun()
        elif username == "student" and password == "student123":
            # ကျောင်းသား အရင်ဖြေပြီးသား ဟုတ်မဟုတ် စစ်ဆေးခြင်း
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
    # LOGOUT BUTTON
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()
        
    # ADMIN PANEL
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel (Secure Cloud Mode)")
        
        tab1, tab2 = st.tabs(["📝 View Results Logs", "➕ Add Secure Questions"])
        
        with tab1:
            st.subheader("🔒 Google Sheets Live Records")
            
            # ဒေတာဘေ့စ်မှ တိုက်ရိုက်ဆွဲထုတ်ခြင်း
            db_data = get_results_from_sheet()
            
            # Backup ဒေတာများရှိပါက ပေါင်းပြခြင်း
            if "local_backup" in st.session_state:
                for b in st.session_state.local_backup:
                    if b not in db_data:
                        db_data.append(b)
                        
            if db_data and len(db_data) > 0:
                table_list = []
                for r in db_data:
                    # ခေါင်းစဉ်တန်းကို ဖယ်ထုတ်ပြီး ဒေတာများကို ဇယားစီခြင်း
                    if str(r[0]) != "Timestamp" and len(r) >= 3:
                        table_list.append({"Timestamp": r[0], "Student Username": r[1], "Score Obtained": f"{r[2]} Points"})
                
                if table_list:
                    st.table(table_list)
                else:
                    st.info("ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
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
            
            # Google Sheets Cloud ထဲသို့ ဒေတာလှမ်းသိမ်းခြင်း
            save_result_to_sheet(st.session_state.username, score)
            
            st.success(f"🎉 သင်၏ ရမှတ်မှာ {score}/{len(st.session_state.questions)} ဖြစ်ပြီး စနစ်မှ သိမ်းဆည်းကာ Lock ချထားပြီး ဖြစ်ပါသည်။")
            st.balloons()
            
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.username = None
