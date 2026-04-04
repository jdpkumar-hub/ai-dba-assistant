import streamlit as st
from openai import OpenAI
from supabase import create_client

from auth import login, signup
from analyze import analyze_page
from history import history_page
from admin import admin_page

# Setup
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "history" not in st.session_state:
    st.session_state.history = []

# Auth
if not st.session_state.logged_in:

    menu = st.sidebar.selectbox("Account", ["Login", "Sign Up"])

    if menu == "Login":
        login(supabase)
    else:
        signup(supabase)

else:
    st.sidebar.write(f"👤 {st.session_state.username}")

    page = st.sidebar.radio("Menu", ["Analyze", "History", "Admin"])

    if page == "Analyze":
        analyze_page(client)
    elif page == "History":
        history_page()
    elif page == "Admin":
        admin_page(supabase, st.session_state.username)