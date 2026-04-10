import streamlit as st
from supabase import create_client

# ==============================
# 🔐 Supabase Config
# ==============================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==============================
# 🚀 GOOGLE LOGIN (Direct Flow)
# ==============================
def google_login():
    redirect_url = "https://ai-oracle-assistant.streamlit.app"

    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": redirect_url
        }
    })

    # ✅ FIX HERE
    return res.url


# ==============================
# 📧 EMAIL LOGIN
# ==============================
def email_login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return res
    except Exception as e:
        return None


# ==============================
# 📝 SIGNUP
# ==============================
def signup(email, password):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return res
    except Exception:
        return None


# ==============================
# 🔑 RESET PASSWORD
# ==============================
def reset_password(email):
    try:
        supabase.auth.reset_password_email(email)
        return True
    except Exception:
        return False


# ==============================
# 🔓 LOGOUT
# ==============================
def logout():
    supabase.auth.sign_out()
    st.session_state["user"] = None
    st.success("Logged out successfully")


# ==============================
# 🧠 LOGIN UI (MAIN FUNCTION)
# ==============================
def login():
    st.title("🔐 Login")

    # --------------------------
    # GOOGLE LOGIN
    # --------------------------
    st.subheader("Continue with Google")

    if st.button("🔵 Continue with Google"):
        url = google_login()

        # 🔥 BONUS: AUTO REDIRECT (NO CLICK NEEDED)
        st.markdown(
            f'<meta http-equiv="refresh" content="0;url={url}">',
            unsafe_allow_html=True
        )

    st.divider()

    # --------------------------
    # EMAIL LOGIN
    # --------------------------
    st.subheader("Or login with Email")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = email_login(email, password)

        if user:
            st.session_state["user"] = user
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid email or password ❌")

    st.divider()

    # --------------------------
    # SIGNUP
    # --------------------------
    st.subheader("New user? Sign up")

    new_email = st.text_input("New Email")
    new_password = st.text_input("New Password", type="password")

    if st.button("Sign Up"):
        res = signup(new_email, new_password)

        if res:
            st.success("Signup successful! Please login.")
        else:
            st.error("Signup failed")

    st.divider()

    # --------------------------
    # RESET PASSWORD
    # --------------------------
    st.subheader("Forgot Password")

    reset_email = st.text_input("Enter your email to reset password")

    if st.button("Reset Password"):
        if reset_password(reset_email):
            st.success("Password reset email sent 📩")
        else:
            st.error("Error sending reset email")