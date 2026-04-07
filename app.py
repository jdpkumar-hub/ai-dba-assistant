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

st.sidebar.image("logo.png", use_container_width=True)
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
# SESSION INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================
# STRIPE SUCCESS HANDLER
# =========================
   
# =========================
# STRIPE SUCCESS HANDLER (FIXED)
# =========================
query_params = st.query_params

# Prevent infinite loop
if query_params.get("success") == "true" and not st.session_state.get("payment_handled"):

    st.session_state.payment_handled = True

    st.success("🎉 **Payment Successful! Your account is upgraded to PRO 🚀**")
    st.markdown("### 🔐 **Please login again to continue**")

    # Clear query params safely
    st.query_params.clear()

    # Reset session
    st.session_state.logged_in = False
    st.session_state.username = ""

    # DO NOT LOOP RERUN
    st.stop()

# =========================
# AUTH SECTION
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

    user_data = supabase.table("users").select("*").eq(
        "email", st.session_state.username
    ).execute()

    user = user_data.data[0] if user_data.data else {}

    user_role = user.get("role", "user")
    usage_count = user.get("usage_count", 0)

    st.session_state.user_role = user_role
    st.session_state.usage_count = usage_count

    # ROLE
    if user_role == "admin":
        st.sidebar.success("👑 Admin")
    elif user_role == "pro":
        st.sidebar.success("💳 Pro User")
    else:
        st.sidebar.info("👤 Free User")

    # USAGE
    st.sidebar.markdown("### 📊 Usage")

    if user_role == "user":
        st.sidebar.write(f"{usage_count} / 5 used")
    else:
        st.sidebar.write("Unlimited 🚀")

    # UPGRADE
    if user_role == "user":

        st.sidebar.markdown("---")

        checkout_url = payments.create_checkout_session(
            st.session_state.username
        )

        st.sidebar.markdown(
            f"""
            <a href="{checkout_url}" target="_self">
                <button style="
                    background-color:#ff4b4b;
                    color:white;
                    padding:10px 20px;
                    border:none;
                    border-radius:8px;
                    font-size:16px;
                    cursor:pointer;">
                    🚀 Upgrade to Pro
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.success("🎉 You are already Pro!")

    # MENU
    if user_role == "admin":
        page = st.sidebar.radio("Menu", ["Analyze", "History", "Admin"])
    else:
        page = st.sidebar.radio("Menu", ["Analyze", "History"])

    # LOGOUT
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # WARNING
    if user_role == "user":
        st.warning("⚠️ **Free version: Upgrade to Pro for full features 💳**")

    # PAGES
    if page == "Analyze":
        analyze_page(client, supabase)

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
}
</style>
<div class="footer">
© AI Oracle DBA Assistant 🚀
</div>
""", unsafe_allow_html=True)