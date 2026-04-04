# =========================
# 🚀 MAIN APP
# =========================
else:

    st.sidebar.title("🚀 AI DBA Assistant")

    # 👤 Show logged-in user
    st.sidebar.write(f"👤 {st.session_state.username}")

    st.sidebar.markdown("---")

    # 🔐 ROLE BASED MENU
    if st.session_state.username == "admin":
        page = st.sidebar.radio("📌 Menu", ["Analyze", "History", "Admin"])
    else:
        page = st.sidebar.radio("📌 Menu", ["Analyze", "History"])

    # 🚪 LOGOUT
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # =========================
    # 🔍 ANALYZE
    # =========================
    if page == "Analyze":
        analyze_page(client)

    # =========================
    # 💬 HISTORY
    # =========================
    elif page == "History":
        history_page()

    # =========================
    # 👑 ADMIN (ONLY ADMIN)
    # =========================
    elif page == "Admin":
        admin_page(supabase, st.session_state.username)