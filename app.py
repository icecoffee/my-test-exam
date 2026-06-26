# --- ADMIN PANEL ---
    if st.session_state.user_role == "admin":
        # 💡 ခေါင်းစီး (Title) ကို တစ်ကြိမ်သာ သုံးပါ
        st.title("👩‍🏫 Admin Control Panel (Secure Mode)")
        
        # Sidebar တွင် ခလုတ်တစ်ခုတည်းသာ ထားရှိခြင်း (သန့်ရှင်းစေရန်)
        st.sidebar.subheader("⚙️ System Control")
        if st.sidebar.button("♻️ FULL SYSTEM RESET", type="primary"):
            st.session_state.global_results_pool = []
            if "submitted" in st.session_state: st.session_state.submitted = False
            st.sidebar.success("System Reset Successfully!")
            st.rerun()
        
        # Tabs အပိုင်း (ဒီအောက်မှာ Title ထပ်မထည့်ပါနှင့်)
        tab1, tab2 = st.tabs(["📝 View Results Logs", "➕ Add Secure Questions"])
        with tab1:
            st.subheader("🔒 Terminal Live Records")
            # ... ကျန်ရှိသော Log display ကုဒ်များ ...
