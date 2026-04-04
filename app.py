import streamlit as st
from openai import OpenAI
from supabase import create_client
from auth import (
    login,
    signup,
    verify_otp,
    reset_password_request,
    reset_password_confirm
)

from analyze import analyze_page
from history import history_page
from admin import admin_page

# =========================
# 🎨 CONFIG
# =========================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# Sidebar branding (ONLY ONCE ✅)
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("## AI DBA Assistant")
st.sidebar.markdown("---")

# =========================
# 🔑 SETUP
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# 🧠 SESSION INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================
# 🔐 AUTH FLOW
# =========================
if not st.session_state.logged_in:

    menu = st.sidebar.selectbox("Select", ["Login", "Sign Up", "Reset Password"])

    # 🔐 Signup OTP
    if st.session_state.get("show_otp"):
        verify_otp(supabase)

    # 🔐 Reset OTP
    elif st.session_state.get("show_reset_otp"):
        reset_password_confirm(supabase)

    elif menu == "Login":
        login(supabase)

    elif menu == "Sign Up":
        signup(supabase)

    elif menu == "Reset Password":
        reset_password_request(supabase)

# =========================
# 🚀 MAIN APP
# =========================
else:

    # 👤 User Info
    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.markdown("---")

    # 🔐 Role fetch
    try:
        user_data = supabase.table("users").select("role").eq(
            "email", st.session_state.username
        ).execute()

        user_role = user_data.data[0]["role"] if user_data.data else "user"

    except:
        user_role = "user"

    # 👑 Role label
    if user_role == "admin":
        st.sidebar.success("👑 Admin")
    else:
        st.sidebar.info("👤 User")

    # 📌 Menu
    if user_role == "admin":
        page = st.sidebar.radio("📌 Menu", ["Analyze", "History", "Admin"])
    else:
        page = st.sidebar.radio("📌 Menu", ["Analyze", "History"])

    # 🚪 Logout
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
    # 👑 ADMIN
    # =========================
    elif page == "Admin":
        admin_page(supabase, st.session_state.username)

# =========================
# 📌 FOOTER
# =========================
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 10px;
    left: 20px;
    width: 100%;
    color: gray;
    font-size: 14px;
}
</style>

<div class="footer">
© AI Oracle DBA Assistant | Built by Pradarshan Kumar JD 🚀
</div>
""", unsafe_allow_html=True)