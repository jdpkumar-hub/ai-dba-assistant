import streamlit as st
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlcXVxc2J2aHlkdnVnaWZldmhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUyNzAzOTUsImV4cCI6MjA5MDg0NjM5NX0.AMTQgSM56qdYy3VOmq9frtBzg_a6TC7c03rp4YgH8cw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-dba-assistant.streamlit.app"

def login():
    st.subheader("Login")

    # ================= EMAIL LOGIN =================
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

    # ================= GOOGLE LOGIN =================
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": REDIRECT_URL}
    })

    if res.url:
        st.link_button("🔵 Continue with Google", res.url)
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
query_params = st.query_params

if query_params.get("type") == "recovery":
    st.title("🔑 Reset Your Password")

    # ✅ STEP 1: Extract tokens
    access_token = query_params.get("access_token")
    refresh_token = query_params.get("refresh_token")

    # ✅ STEP 2: Create session manually
    if access_token and refresh_token:
        try:
            supabase.auth.set_session({
                "access_token": access_token,
                "refresh_token": refresh_token
            })
        except Exception as e:
            st.error(f"Session setup failed: {e}")

    # UI
    new_password = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        try:
            supabase.auth.update_user({
                "password": new_password
            })

            st.success("✅ Password updated successfully!")
            st.info("Please login with your new password.")

        except Exception as e:
            st.error("❌ Failed to update password")
            st.write(e)

    st.stop()

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