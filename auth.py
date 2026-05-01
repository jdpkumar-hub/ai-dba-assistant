import streamlit as st
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "sb_publishable_ZOfGu0PLriJqtJLdmk6Bkg_mJ3HrURB"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-dba-assistant.streamlit.app"

# ================= LOGIN =================
def login():
    st.markdown("## 🔐 Login")

    email = st.text_input("Email", key="login_email")

    col1, col2 = st.columns(2)

    # ===== OTP LOGIN =====
    with col1:
        if st.button("Send OTP"):
            try:
                supabase.auth.sign_in_with_otp({"email": email})
                st.session_state.otp_sent = True
                st.success("📩 OTP sent to your email")
            except Exception as e:
                st.error("Failed to send OTP")

    # ===== PASSWORD LOGIN (optional fallback) =====
    with col2:
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login with Password"):
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

    st.divider()

    # ===== GOOGLE LOGIN =====
    if st.button("🔵 Continue with Google"):
        try:
            res = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {"redirect_to": REDIRECT_URL}
            })
            st.link_button("👉 Click to login with Google", res.url)
        except Exception:
            st.error("Google login failed")

# ================= SIGNUP =================
def signup():
    st.markdown("## 🆕 Create Account")

    email = st.text_input("Email", key="signup_email")

    if st.button("Send Signup OTP"):
        try:
            supabase.auth.sign_in_with_otp({
                "email": email,
                "options": {
                    "email_redirect_to": REDIRECT_URL
                }
            })
            st.success("📩 Verification email sent")
        except Exception:
            st.error("Failed to send OTP")

# ================= RESET PASSWORD =================
def reset_password():
    st.markdown("## 🔑 Reset Password")

    email = st.text_input("Email", key="reset_email")

    if st.button("Send Reset Link"):
        try:
            supabase.auth.reset_password_for_email(
                email,
                {"redirect_to": REDIRECT_URL}
            )
            st.success("📩 Password reset email sent")
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