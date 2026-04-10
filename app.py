import streamlit as st
from supabase_client import supabase
from auth import login
from dashboard import dashboard
from chat import chat_ui

st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# ---------------------------
# SESSION INIT
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------------------
# TOKEN HANDLING (SECURE)
# ---------------------------
query_params = st.query_params

if "token" in query_params:
    token = query_params["token"]

    try:
        user = supabase.auth.get_user(token)
        if user:
            st.session_state.user = user.user
            st.query_params.clear()  # remove token from URL
    except:
        st.error("Invalid session")

# ---------------------------
# SIDEBAR
# ---------------------------
menu = st.sidebar.selectbox(
    "Select",
    ["Login", "Dashboard", "AI Chat"]
)

# ---------------------------
# ROUTING
# ---------------------------
if st.session_state.user:
    st.sidebar.success(f"👤 {st.session_state.user.email}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    if menu == "Dashboard":
        dashboard()

    elif menu == "AI Chat":
        chat_ui()

else:
    login()