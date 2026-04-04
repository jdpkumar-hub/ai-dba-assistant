import streamlit as st
from utils import is_strong_password, hash_password, verify_password
import random
import smtplib
from email.mime.text import MIMEText

# =========================
# 📧 SEND OTP EMAIL (DEBUG VERSION)
# =========================
def send_otp_email(to_email, otp):

    sender = st.secrets["EMAIL_ADDRESS"]
    password = st.secrets["EMAIL_PASSWORD"]

    subject = "Your OTP Code - AI DBA Assistant"
    body = f"Your OTP is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    # 🔍 DEBUG (TEMPORARY)
    st.write("📧 Sender:", sender)
    st.write("🔑 Password length:", len(password))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # 🔍 DEBUG LOGIN STEP
        st.write("Connecting to Gmail SMTP...")

        server.login(sender, password)

        st.write("Login successful ✅")

        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        st.error("Email sending failed ❌")
        st.write("Error:", e)
        return False


# =========================
# 📝 SIGNUP + OTP
# =========================
def signup(supabase):
    st.title("📝 Sign Up")

    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Create Account"):

        if not email or not password:
            st.warning("Please fill all fields")
            return

        if not is_strong_password(password):
            st.warning("Weak password")
            return

        result = supabase.table("users").select("*").eq("email", email).execute()

        if result.data:
            st.warning("User already exists")
            return

        # Save temp data
        st.session_state.temp_email = email
        st.session_state.temp_password = hash_password(password)

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        st.session_state.otp = otp

        # Send email
        sent = send_otp_email(email, otp)

        if sent:
            st.success("OTP sent to your email 📧")
            st.session_state.show_otp = True  
            st.rerun()   # ✅ THIS FIXES YOUR ISSUE
        else:
            st.error("Failed to send OTP")


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
                "password": st.session_state.temp_password
            }).execute()

            st.session_state.logged_in = True
            st.session_state.username = st.session_state.temp_email
            st.session_state.show_otp = False

            st.success("Account created & verified ✅")
            st.rerun()

        else:
            st.error("Invalid OTP ❌")


# =========================
# 🔑 RESET PASSWORD
# =========================
def reset_password(supabase):
    st.title("🔑 Reset Password")

    email = st.text_input("Email")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Reset Password"):

        if not is_strong_password(new_pass):
            st.warning("Weak password")
            return

        hashed = hash_password(new_pass)

        supabase.table("users").update({
            "password": hashed
        }).eq("email", email).execute()

        st.success("Password updated ✅")


# =========================
# 🔐 LOGIN
# =========================
def login(supabase):
    st.title("🔐 Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):

        if not email or not password:
            st.warning("Enter credentials")
            return

        result = supabase.table("users").select("*").eq("email", email).execute()

        if result.data:
            stored_password = result.data[0]["password"]

            if verify_password(password, stored_password):
                st.session_state.logged_in = True
                st.session_state.username = email
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Wrong password")
        else:
            st.error("User not found")