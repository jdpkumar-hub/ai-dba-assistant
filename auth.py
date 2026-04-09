import streamlit as st
from utils import is_strong_password, hash_password, verify_password
import random
import smtplib
from email.mime.text import MIMEText
import time

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

    email = st.text_input("Email", key="signup_email")

    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name")
    with col2:
        last_name = st.text_input("Last Name")

    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

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

    remaining = int(st.session_state.get("otp_expiry", 0) - time.time())

    if remaining > 0:
        st.info(f"⏳ Expires in {remaining}s")
    else:
        st.error("OTP expired ❌")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Verify OTP"):

            if time.time() > st.session_state.get("otp_expiry", 0):
                st.error("OTP expired")
                return

            if user_otp == st.session_state.get("otp"):

                # ✅ FIXED INDENTATION HERE
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

    with col2:
        if st.button("Resend OTP"):
            otp = str(random.randint(100000, 999999))
            st.session_state.otp = otp
            st.session_state.otp_expiry = time.time() + 600
            send_otp_email(st.session_state.temp_email, otp)
            st.success("OTP resent 📧")
            st.rerun()


# =========================
# 🔑 RESET REQUEST
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
# 🔐 RESET CONFIRM
# =========================
def reset_password_confirm(supabase):
    st.title("🔐 Reset Password")

    otp = st.text_input("Enter OTP")
    new_pass = st.text_input("New Password", type="password")
    confirm_pass = st.text_input("Confirm Password", type="password")

    remaining = int(st.session_state.get("reset_expiry", 0) - time.time())

    if remaining > 0:
        st.info(f"⏳ Expires in {remaining}s")
    else:
        st.error("OTP expired ❌")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update Password"):

            if time.time() > st.session_state.get("reset_expiry", 0):
                st.error("OTP expired")
                return

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

            st.session_state.logged_in = True
            st.session_state.username = st.session_state.reset_email

            st.session_state.show_reset_otp = False
            st.session_state.pop("reset_otp", None)
            st.session_state.pop("reset_expiry", None)

            st.success("Password updated & logged in ✅")
            st.rerun()

    with col2:
        if st.button("Resend OTP"):
            otp = str(random.randint(100000, 999999))
            st.session_state.reset_otp = otp
            st.session_state.reset_expiry = time.time() + 600
            send_otp_email(st.session_state.reset_email, otp)
            st.success("OTP resent 📧")
            st.rerun()


# =========================
# 🔐 LOGIN
# =========================
def login(supabase):
    st.title("🔐 Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

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