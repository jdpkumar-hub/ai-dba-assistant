import streamlit as st

def admin_page(supabase, username):
    st.header("👑 Admin")

    if username != "admin":
        st.error("Access denied")
        return

    result = supabase.table("users").select("username").execute()

    for user in result.data:
        st.write(user["username"])