import streamlit as st
from supabase import create_client

# -------------------------------
# CONFIG
# -------------------------------
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "sb_publishable_ZOfGu0PLriJqtJLdmk6Bkg_mJ3HrURB"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-oracle-assistant.streamlit.app"

# -------------------------------
# LOGIN (EMAIL + GOOGLE)
# -------------------------------
def login():
    st.markdown("## 🔐 Login")

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

        except Exception as e:
            st.error("Invalid credentials")

    st.divider()

    # Google Login
    if st.button("🔵 Continue with Google"):
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": REDIRECT_URL
            }
        })

        if res.url:
            st.markdown(f"[Click here if not redirected]({res.url})")
            st.markdown(
                f"""<script>window.location.href="{res.url}"</script>""",
                unsafe_allow_html=True
            )

# -------------------------------
# SIGNUP (WITH CONFIRM PASSWORD)
# -------------------------------
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

            st.success("Account created! Check email for verification link")

        except Exception as e:
            st.error("Signup failed")

# -------------------------------
# RESET PASSWORD
# -------------------------------
def reset_password():
    st.markdown("## 🔑 Reset Password")

    email = st.text_input("Email", key="reset_email")

    if st.button("Send Reset Link"):
        try:
            supabase.auth.reset_password_email(email)
            st.success("Reset link sent to email")
        except:
            st.error("Failed to send reset email")

# -------------------------------
# GET USER
# -------------------------------
def get_user():
    try:
        res = supabase.auth.get_user()
        return res.user if res else None
    except:
        return None

# -------------------------------
# LOGOUT
# -------------------------------
def logout():
    if st.button("🚪 Logout"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()