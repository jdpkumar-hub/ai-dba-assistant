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
# 🔑 RESET PASSWORD SCREEN
# -------------------------------
if st.session_state.get("reset_mode"):

    st.title("🔑 Set New Password")

    new_pass = st.text_input("New Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):
        if new_pass != confirm_pass:
            st.error("Passwords do not match")
        else:
            try:
                supabase.auth.update_user({
                    "password": new_pass
                })
                st.success("Password updated successfully!")
                st.session_state.reset_mode = False
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.stop()

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

        except Exception:
            st.error("Invalid credentials")

    st.divider()

    # -------------------------------
    # Google Login (FIXED)
    # -------------------------------
    # Google Login
# Google Login Button (FIXED)
if st.button("🔵 Continue with Google"):

    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": "https://ai-oracle-assistant.streamlit.app"
        }
    })

    if res.url:
        st.markdown(
            f"<script>window.location.href='{res.url}'</script>",
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
            res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": REDIRECT_URL
                }
            })

            if res.user:
                st.success("Account created! Check your email for verification link")
            else:
                st.error("Signup failed")

        except Exception as e:
            st.error(f"Error: {e}")

# -------------------------------
# RESET PASSWORD
# -------------------------------
def reset_password():
    st.markdown("## 🔑 Reset Password")

    email = st.text_input("Email", key="reset_email")

    if st.button("Send Reset Link"):
        try:
            supabase.auth.reset_password_email(
                email,
                options={"redirect_to": REDIRECT_URL}
            )
            st.success("Reset link sent to email")

        except Exception as e:
            st.error(f"Failed to send reset email: {e}")

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