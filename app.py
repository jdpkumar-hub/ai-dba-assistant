import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase

# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# ================= PASSWORD RESET HANDLER =================
query = st.query_params

if query.get("type") == "recovery":

    st.title("🔑 Reset Your Password")

    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):

        if new_password != confirm_password:
            st.error("Passwords do not match")
        else:
            try:
                supabase.auth.update_user({
                    "password": new_password
                })

                st.success("✅ Password updated successfully")
                st.query_params.clear()

            except Exception as e:
                st.error("Reset failed")
                st.write(e)

    st.stop()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

# ================= LOGIN SCREEN =================
if not user:

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("image/logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization")

    with col2:
        tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Reset"])

        with tab1:
            login()

        with tab2:
            signup()

        with tab3:
            reset_password()

    st.stop()

# ================= APP (UNCHANGED) =================
st.sidebar.success(user.email)

if st.sidebar.button("Logout"):
    logout()

st.title("Welcome to AI DBA Assistant")