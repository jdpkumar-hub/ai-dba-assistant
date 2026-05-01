import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "YOUR_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-dba-assistant.streamlit.app"

# ================= LOGIN =================
def login():
    email = st.text_input("Email", key="login_email")

    if st.button("Send OTP"):
        supabase.auth.sign_in_with_otp({"email": email})
        st.success("OTP sent")

# ================= SIGNUP =================
def signup():
    email = st.text_input("Email", key="signup_email")

    if st.button("Signup OTP"):
        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {"email_redirect_to": REDIRECT_URL}
        })
        st.success("Check email")

# ================= RESET =================
def reset_password():
    email = st.text_input("Email", key="reset_email")

    if st.button("Send Reset Link"):
        supabase.auth.reset_password_for_email(
            email,
            {"redirect_to": REDIRECT_URL + "/?type=recovery"}
        )
        st.success("Reset email sent")

# ================= USER =================
def get_user():
    try:
        session = supabase.auth.get_session()
        return session.user if session else None
    except:
        return None

# ================= LOGOUT =================
def logout():
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()