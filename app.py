import streamlit as st
import pandas as pd

# Google Sheet ID
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"

# Google Sheet ကနေ CSV အဖြစ် တိုက်ရိုက်ဆွဲထုတ်မယ့် URL များ
# (gid=0 သည် Sheet1 ဖြစ်ပြီး မေးခွန်း/ရလဒ်များအတွက် အဆင်ပြေအောင် သေချာစစ်ပါ)
URL_USERS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet3"
URL_QUESTIONS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet2"

st.set_page_config(page_title="DCS Exam System", layout="centered")

# --- ယူဇာများကို Google Sheet (Sheet3) မှ အလိုအလျောက်ဆွဲယူခြင်း ---
@st.cache_data(ttl=60)
def load_users():
    try:
        df = pd.read_csv(URL_USERS)
        # Username နဲ့ Password ကို Dictionary အဖြစ်ပြောင်း
        return dict(zip(df['Username'].astype(str), df['Password'].astype(str)))
    except:
        return {"admin": "admin123"} # အဆင်မပြေရင် ဒါပဲသုံး

# --- မေးခွန်းများကို Google Sheet (Sheet2) မှဆွဲယူခြင်း ---
@st.cache_data(ttl=60)
def load_questions():
    try:
        return pd.read_csv(URL_QUESTIONS)
    except:
        return pd.DataFrame()

# --- Login Logic ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    users = load_users()
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()
        elif user in users and pwd == users[user]:
            st.session_state.logged_in = True
            st.session_state.role = "student"
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Login Failed")
else:
    if st.session_state.role == "admin":
        st.title("Admin Panel")
        st.write("Google Sheets မှ ရလဒ်များ:")
        # Admin က ဘာမှမလုပ်ရဘဲ Sheet ထဲမှာ ရှိတာတွေ ပေါ်လာမယ်
        st.table(pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"))
    else:
        st.title(f"Welcome {st.session_state.username}")
        questions = load_questions()
        if not questions.empty:
            st.table(questions) # မေးခွန်းများပေါ်လာမယ်
        else:
            st.warning("မေးခွန်းများ မတင်ရသေးပါ။")
