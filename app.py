import streamlit as st
from auth import login

st.set_page_config(page_title="AI DBA Assistant")

# ✅ Initialize session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ Capture token from URL
query_params = st.query_params

if "token" in query_params:
    st.session_state.logged_in = True

# Sidebar
option = st.sidebar.selectbox("Select", ["Login", "Dashboard"])

# ✅ If logged in → show dashboard
if st.session_state.logged_in:
    st.title("📊 Analysis Dashboard")
    st.success("You are logged in ✅")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ❌ If not logged in → show login
else:
    login()