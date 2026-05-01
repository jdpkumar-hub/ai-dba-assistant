import streamlit as st
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlcXVxc2J2aHlkdnVnaWZldmhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUyNzAzOTUsImV4cCI6MjA5MDg0NjM5NX0.AMTQgSM56qdYy3VOmq9frtBzg_a6TC7c03rp4YgH8cw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
st.write("Secrets loaded:", "SUPABASE_KEY" in st.secrets)
REDIRECT_URL = "https://ai-dba-assistant.streamlit.app"

# ================= LOGIN =================
def login():
    st.subheader("Login")

    # ✅ Google OAuth (ONLY ONE METHOD)
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": REDIRECT_URL}
    })

    if res.url:
        st.link_button("🔵 Continue with Google", res.url)

    st.divider()

    # Email login
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if res.user:
                st.session_state.user = res.user
                st.success("Login successful")
                st.rerun()

        except Exception:
            st.error("Invalid credentials")

# ================= SIGNUP =================
def signup():
    st.markdown("## 🆕 Create Account")

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pass")
    confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Create Account"):
        if password != confirm:
            st.error("Passwords do not match")
            return

        try:
            supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            st.success("Check email for verification link")
        except Exception:
            st.error("Signup failed")

# ================= RESET =================
def reset_password():
    st.markdown("## 🔑 Reset Password")

    email = st.text_input("Email", key="reset_email")

    if st.button("Send Reset Link"):
        try:
            supabase.auth.reset_password_for_email(email)
            st.success("Reset link sent")
        except Exception:
            st.error("Failed to send email")

# ================= GET USER =================
def get_user():
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            return session.user
        return None
    except Exception:
        return None

# ================= LOGOUT =================
def logout():
    if st.button("🚪 Logout"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.clear()
        st.rerun()