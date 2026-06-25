import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- GOOGLE SHEET DATABASE CONFIGIVITY ---
SHEET_ID = "1ytBPXMKDwY2CY1hkEBxL6bCVwgr-GkmhzDFpvSVTIkA"

# Google Sheet မှ Data များ ဆွဲဖတ်ရန် URL များ
CSV_RESULTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
CSV_QUESTIONS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=2071758052"
CSV_USERS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=Sheet3"

# Google Sheet (Sheet1) ထဲသို့ ဒေတာ တိုက်ရိုက်လှမ်းသိမ်းရန် Web App URL
GOOGLE_FORM_URL = f"https://docs.google.com/forms/d/e/1FAIpQLSclK7tUfS_R52OaOunA-bE_P7m84_j9iU5RstWb7pAic9_U4A/formResponse"

# --- 1. SYSTEM INITIALIZATION ---
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

def get_results_from_sheet():
    try:
        # Cache ငြိမ
