import streamlit as st
from openai import OpenAI
from supabase import create_client

from auth import login
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
# 🔥 AUTO LOGIN FROM REACT TOKEN
# =========================
query_params = st.query_params
token = query_params.get("token")

# handle list case
if isinstance(token, list):
    token = token[0]

if token:
    try:
        user = supabase.auth.get_user(jwt=token)

        if user and user.user:
            st.session_state.logged_in = True
            st.session_state.username = user.user.email

            # clean URL after login
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
# AUTH FLOW (FIXED ✅)
# =========================
if not st.session_state.logged_in:

    # ✅ ONLY LOGIN (removed broken features)
    menu = st.sidebar.selectbox("Select", ["Login"])

    if menu == "Login":
        login(supabase)

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