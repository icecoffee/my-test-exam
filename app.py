import streamlit as st
import pandas as pd

# Google Sheet ID (ဆရာ့ Sheet ID အမှန်ဖြစ်ပါစေ)
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"
# CSV အဖြစ် တိုက်ရိုက်ဆွဲထုတ်မည့် URL (Sheet1 သည် ရလဒ်များ၊ Sheet3 သည် User List)
URL_RESULTS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
URL_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"

# --- LOGIN & STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

def show_admin():
    st.title("👩‍🏫 Admin Control Panel")
    if st.button("Refresh Results"): st.rerun()
    try:
        # Sheet1 မှ အဖြေများကို ဖတ်ခြင်း
        df = pd.read_csv(URL_RESULTS)
        if not df.empty:
            st.table(df)
        else:
            st.write("Sheet1 ထဲတွင် ဒေတာမရှိသေးပါ။")
    except Exception as e:
        st.error("Google Sheet ချိတ်ဆက်မှု မအောင်မြင်ပါ။ Sharing Setting ကို 'Anyone with the link' ဖြစ်အောင် လုပ်ထားပါ။")

def show_student():
    st.title(f"✍️ Exam Terminal: {st.session_state.username}")
    st.write("စာမေးပွဲဖြေဆိုရန် အဆင်သင့်ဖြစ်ပါပြီ။")

# --- MAIN ---
if not st.session_state.logged_in:
    st.title("🔐 Secure Exam Terminal")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        # အဆင့် (၁): Sheet3 မှ User စာရင်းကို အလိုအလျောက်ဖတ်ခြင်း
        df_users = pd.read_csv(URL_USERS)
        # အဆင့် (၂): Login စစ်ဆေးခြင်း
        user_check = df_users[(df_users['Username'] == user) & (df_users['Password'].astype(str) == pwd)]
        
        if user == "admin" and pwd == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.session_state.username = user
            st.rerun()
        elif not user_check.empty:
            st.session_state.logged_in = True
            st.session_state.role = "student"
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Invalid Credentials!")
else:
    if st.session_state.role == "admin": show_admin()
    else: show_student()
