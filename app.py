import streamlit as st
from auth import login

st.set_page_config(page_title="AI DBA Assistant")

# Sidebar
option = st.sidebar.selectbox("Select", ["Login"])

# Main
if option == "Login":
    login()