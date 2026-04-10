import streamlit as st
from openai import OpenAI
from supabase import create_client

from auth import login
#from auth import (
 #   login,
 #   signup,
#    verify_otp,
 #   reset_password_request,
 #   reset_password_confirm
#)

from analyze import analyze_page
from history import history_page
from admin import admin_page

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# =========================
# SETUP
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# 🔥 AUTO LOGIN FROM REACT TOKEN (FINAL FIX)
# =========================
query_params = st.query_params
token = query_params.get("token")

# ✅ Fix: handle list
if isinstance(token, list):
    token = token[0]

# 🔍 DEBUG (remove later if needed)
# st.write("TOKEN DEBUG:", token)

if token:
    try:
        # ✅ Correct Supabase call
        user = supabase.auth.get_user(jwt=token)

        # st.write("USER DEBUG:", user)

        if user and user.user:
            st.session_state.logged_in = True
            st.session_state.username = user.user.email

            # ✅ Clean URL
            st.query_params.clear()

            st.success("Auto Login Success ✅")

            st.rerun()

    except Exception as e:
        st.error(f"Token Error: {e}")

# =========================
# SESSION INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Analyze"

# =========================
# SIDEBAR
# =========================
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("## AI DBA Assistant")
st.sidebar.markdown("---")

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

    try:
        user_data = supabase.table("users").select("role").eq(
            "email", st.session_state.username
        ).execute()

        user_role = user_data.data[0]["role"] if user_data.data else "user"
    except:
        user_role = "user"

    if user_role == "admin":
        page = st.sidebar.radio("Menu", ["Analyze", "History", "Admin"])
    else:
        page = st.sidebar.radio("Menu", ["Analyze", "History"])

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if page == "Analyze":
        analyze_page(client)

    elif page == "History":
        history_page()

    elif page == "Admin":
        admin_page(supabase, st.session_state.username)