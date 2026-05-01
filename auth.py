import streamlit as st
from supabase import create_client

# -------------------------------
# CONFIG
# -------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-oracle-assistant.streamlit.app"

# -------------------------------
# SESSION INIT (PREVENT LEAK)
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.user_email = None


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
                # ✅ SAFE SESSION STORE
                st.session_state.user = res.user
                st.session_state.user_email = res.user.email

                st.success("Login successful")
                st.rerun()

        except Exception:
            st.error("Invalid credentials")

    st.divider()

    # ---------------- GOOGLE LOGIN ----------------
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
# SIGNUP
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

        except Exception:
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
# GET USER (FIXED 🔥)
# -------------------------------
def get_user():
    try:
        res = supabase.auth.get_user()

        if res and res.user:
            # ✅ Prevent cross-session leakage
            if st.session_state.user_email != res.user.email:
                st.session_state.user = res.user
                st.session_state.user_email = res.user.email

            return res.user

        return None

    except:
        return None


# -------------------------------
# LOGOUT (FIXED 🔥)
# -------------------------------
def logout():
    if st.button("🚪 Logout"):
        try:
            supabase.auth.sign_out()
        except:
            pass

        # ✅ CLEAR SESSION SAFELY
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()