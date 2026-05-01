# otp_auth.py

import streamlit as st
from auth import supabase


# ===============================
# SEND OTP (SIGNUP)
# ===============================
def send_signup_otp(email):
    try:
        supabase.auth.sign_in_with_otp({
            "email": email,
            "options": {"should_create_user": True}
        })
        st.session_state.signup_email = email
        st.success("OTP sent to email")
    except Exception as e:
        st.error("Failed to send OTP")


# ===============================
# VERIFY OTP (SIGNUP)
# ===============================
def verify_signup_otp(email, otp, password):
    try:
        res = supabase.auth.verify_otp({
            "email": email,
            "token": otp,
            "type": "email"
        })

        if res.user:
            supabase.auth.update_user({
                "password": password
            })
            st.success("Signup successful. You can login now.")
            st.session_state.signup_email = None
    except Exception:
        st.error("Invalid OTP")


# ===============================
# SEND OTP (RESET)
# ===============================
def send_reset_otp(email):
    try:
        supabase.auth.reset_password_email(email)
        st.session_state.reset_email = email
        st.success("Reset link sent to email")
    except Exception:
        st.error("Failed to send reset email")


# ===============================
# OTP UI (SIGNUP)
# ===============================
def signup_with_otp():

    st.subheader("🆕 Signup with OTP")

    email = st.text_input("Email", key="signup_email_input")
    password = st.text_input("Set Password", type="password")

    if st.button("Send OTP"):
        send_signup_otp(email)

    if "signup_email" in st.session_state:
        otp = st.text_input("Enter OTP")

        if st.button("Verify & Create Account"):
            verify_signup_otp(email, otp, password)


# ===============================
# RESET UI
# ===============================
def reset_with_otp():

    st.subheader("🔑 Reset Password")

    email = st.text_input("Email", key="reset_email_input")

    if st.button("Send Reset Link"):
        send_reset_otp(email)

    st.info("Check your email → click reset link → set new password")