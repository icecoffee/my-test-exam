# --- ADMIN PANEL ---
    if st.session_state.user_role == "admin":
        st.title("👩‍🏫 Admin Control Panel (Secure Mode)")
        
        # Sidebar တွင် System Control ခလုတ်တစ်ခုတည်းကိုသာ ထားရှိခြင်း
        st.sidebar.subheader("⚙️ System Control")
        if st.sidebar.button("♻️ FULL SYSTEM RESET", type="primary"):
            st.session_state.global_results_pool = []
            if "submitted" in st.session_state: st.session_state.submitted = False
            st.sidebar.success("Memory Pool & Lock System Cleared!")
            st.rerun()
        
        # Tab အပိုင်း
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
                st.info("💡 ဖြေဆိုထားသော ကျောင်းသား မှတ်တမ်း မရှိသေးပါ။")
                
        with tab2:
            st.subheader("Inject New Question to Pool Permanently")
            st.info("💡 ဤနေရာတွင် မေးခွန်းအသစ်များကို Google Sheet (Sheet2) ထဲသို့ တိုက်ရိုက်သွားရောက်တိုးပေးရပါမည်။")
