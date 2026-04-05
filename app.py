import streamlit as st
from openai import OpenAI
from supabase import create_client

from auth import login, signup, verify_otp, reset_password_request, reset_password_confirm
from analyze import analyze_page
from history import history_page
from admin import admin_page
import payments

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# Sidebar Branding
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("## AI DBA Assistant")
st.sidebar.markdown("---")

# =========================
# SETUP
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# SESSION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================
# HANDLE PAYMENT SUCCESS
# =========================
query_params = st.query_params

if query_params.get("success") == "true" and st.session_state.logged_in:
    st.success("Payment successful 🎉")

    supabase.table("users").update({
        "role": "pro"
    }).eq("email", st.session_state.username).execute()

# =========================
# AUTH FLOW
# =========================
if not st.session_state.logged_in:

    menu = st.sidebar.selectbox("Select", ["Login", "Sign Up", "Reset Password"])

    if st.session_state.get("show_otp"):
        verify_otp(supabase)

    elif st.session_state.get("show_reset_otp"):
        reset_password_confirm(supabase)

    elif menu == "Login":
        login(supabase)

    elif menu == "Sign Up":
        signup(supabase)

    elif menu == "Reset Password":
        reset_password_request(supabase)

# =========================
# MAIN APP
# =========================
else:

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

    # 👑 Role display
    if user_role == "admin":
        st.sidebar.success("👑 Admin")
    elif user_role == "pro":
        st.sidebar.success("💳 Pro User")
    else:
        st.sidebar.info("👤 Free User")

    # =========================
    # 💳 UPGRADE BUTTON (ONLY FREE USERS)
    # =========================
    if user_role == "user":
        st.sidebar.markdown("---")
        st.sidebar.subheader("💳 Upgrade")

        if st.sidebar.button("🚀 Upgrade to Pro"):
            checkout_url = payments.create_checkout_session(
                st.session_state.username
            )
            st.markdown(f"[👉 Click here to Pay]({checkout_url})")

    # =========================
    # MENU
    # =========================
    if user_role == "admin":
        page = st.sidebar.radio("Menu", ["Analyze", "History", "Admin"])
    else:
        page = st.sidebar.radio("Menu", ["Analyze", "History"])

    # =========================
    # LOGOUT
    # =========================
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # =========================
    # PRO LOCK (OPTIONAL)
    # =========================
    if user_role == "user":
        st.warning("⚠️ Free version: Upgrade to Pro for full features 💳")

    # =========================
    # PAGES
    # =========================
    if page == "Analyze":
        analyze_page(client)

    elif page == "History":
        history_page()

    elif page == "Admin":
        admin_page(supabase, st.session_state.username)

# =========================
# FOOTER
# =========================
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 10px;
    left: 350px;
    width: 100%;
    color: gray;
    font-size: 16px;
}
</style>

<div class="footer">
© AI Oracle DBA Assistant | Built by Pradarshan Kumar JD 🚀
</div>
""", unsafe_allow_html=True)