import streamlit as st
from utils import is_strong_password, hash_password, verify_password
import random
import smtplib
from email.mime.text import MIMEText
import time
from urllib.parse import urlencode

SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"

# =========================
# 🔵 GOOGLE LOGIN BUTTON
# =========================
def google_login_button():
    params = {"provider": "google"}
    url = f"{SUPABASE_URL}/auth/v1/authorize?{urlencode(params)}"

    st.markdown(f"""
    <a href="{url}">
    <div style="
        display:flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        border:1px solid #ddd;
        padding:10px;
        border-radius:8px;
        background:white;
        cursor:pointer;">
        <img src="https://developers.google.com/identity/images/g-logo.png" width="20"/>
        <span>Continue with Google</span>
    </div>
    </a>
    """, unsafe_allow_html=True)


# =========================
# 🔵 HANDLE GOOGLE LOGIN
# =========================
def handle_google_login(supabase):
    user = supabase.auth.get_user()

    if user and user.user:
        email = user.user.email

        result = supabase.table("users").select("*").eq("email", email).execute()

        if not result.data:
            supabase.table("users").insert({
                "email": email,
                "password": "google_oauth",
                "first_name": user.user.user_metadata.get("full_name", ""),
                "last_name": ""
            }).execute()

        st.session_state.logged_in = True
        st.session_state.username = email

        st.success("Logged in with Google ✅")
        st.rerun()


# =========================
# 📧 SEND OTP EMAIL
# =========================
def send_otp_email(to_email, otp):
    sender = st.secrets["EMAIL_ADDRESS"]
    password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "OTP - AI DBA Assistant"
    msg["From"] = sender
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error("Email sending failed ❌")
        st.write(e)
        return False


# =========================
# 📝 SIGNUP
# =========================
def signup(supabase):
    st.title("📝 Create Account")

    email = st.text_input("Email")

    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name")
    with col2:
        last_name = st.text_input("Last Name")

    show_password = st.checkbox("Show Password")

    password = st.text_input("Password", type="default" if show_password else "password")
    confirm_password = st.text_input("Confirm Password", type="default" if show_password else "password")

    if st.button("Create Account"):

        if not email or not password or not confirm_password or not first_name:
            st.warning("Please fill all required fields")
            return

        if password != confirm_password:
            st.error("Passwords do not match ❌")
            return

        if not is_strong_password(password):
            st.warning("Weak password")
            return

        result = supabase.table("users").select("*").eq("email", email).execute()

        if result.data:
            st.warning("User already exists")
            return

        st.session_state.temp_email = email
        st.session_state.temp_password = hash_password(password)
        st.session_state.first_name = first_name
        st.session_state.last_name = last_name

        otp = str(random.randint(100000, 999999))
        st.session_state.otp = otp
        st.session_state.otp_expiry = time.time() + 600

        send_otp_email(email, otp)

        st.session_state.show_otp = True
        st.success("OTP sent 📧")
        st.rerun()


# =========================
# 🔐 VERIFY OTP
# =========================
def verify_otp(supabase):
    st.title("🔐 Verify OTP")

    user_otp = st.text_input("Enter OTP")

    if st.button("Verify OTP"):
        if user_otp == st.session_state.get("otp"):

            supabase.table("users").insert({
                "email": st.session_state.temp_email,
                "password": st.session_state.temp_password,
                "first_name": st.session_state.first_name,
                "last_name": st.session_state.last_name
            }).execute()

            st.session_state.logged_in = True
            st.session_state.username = st.session_state.temp_email
            st.session_state.show_otp = False

            st.success("Account created ✅")
            st.rerun()
        else:
            st.error("Invalid OTP ❌")


# =========================
# 🔑 RESET PASSWORD REQUEST
# =========================
def reset_password_request(supabase):
    st.title("🔑 Reset Password")

    email = st.text_input("Email")

    if st.button("Send OTP"):

        result = supabase.table("users").select("*").eq("email", email).execute()

        if not result.data:
            st.error("User not found ❌")
            return

        otp = str(random.randint(100000, 999999))

        st.session_state.reset_email = email
        st.session_state.reset_otp = otp
        st.session_state.reset_expiry = time.time() + 600
        st.session_state.show_reset_otp = True

        send_otp_email(email, otp)

        st.success("OTP sent 📧")
        st.rerun()


# =========================
# 🔐 RESET PASSWORD CONFIRM
# =========================
def reset_password_confirm(supabase):
    st.title("🔐 Reset Password")

    otp = st.text_input("Enter OTP")
    new_pass = st.text_input("New Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):

        if otp != st.session_state.get("reset_otp"):
            st.error("Invalid OTP ❌")
            return

        if new_pass != confirm_pass:
            st.error("Passwords do not match ❌")
            return

        if not is_strong_password(new_pass):
            st.warning("Weak password")
            return

        hashed = hash_password(new_pass)

        supabase.table("users").update({
            "password": hashed
        }).eq("email", st.session_state.reset_email).execute()

        st.session_state.show_reset_otp = False

        st.success("Password updated ✅")
        st.rerun()


# =========================
# 🔐 LOGIN
# =========================
def login(supabase):
    st.title("🔐 Login")

    google_login_button()

    st.divider()

    email = st.text_input("Email")
    show_password = st.checkbox("Show Password")

    password = st.text_input("Password", type="default" if show_password else "password")

    if st.button("Login"):

        result = supabase.table("users").select("*").eq("email", email).execute()

        if result.data:
            stored = result.data[0]["password"]

            if verify_password(password, stored):
                st.session_state.logged_in = True
                st.session_state.username = email
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Wrong password ❌")
        else:
            st.error("User not found ❌")