import streamlit as st
from supabase import create_client

SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "YOUR_KEY"

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
                st.success("📩 OTP sent")
            except:
                st.error("Failed to send OTP")

    # ===== PASSWORD LOGIN =====
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

            except:
                st.error("Invalid credentials")

    st.divider()

    # ===== GOOGLE LOGIN (FIXED) =====
    if st.button("🔵 Continue with Google"):
        try:
            res = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {"redirect_to": REDIRECT_URL}
            })

            # 👉 redirect automatically
            st.markdown(f'<meta http-equiv="refresh" content="0; url={res.url}">', unsafe_allow_html=True)

        except Exception as e:
            st.error("Google login failed")
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