import streamlit as st

# ============================
# 🔐 LOGIN PAGE
# ============================
def login(supabase):

    st.title("🔐 Login")

    # ----------------------------
    # 🔵 GOOGLE LOGIN
    # ----------------------------
    st.markdown("### Continue with Google")

    st.markdown(
        """
        <a href="https://ai-auth-frontend-nine.vercel.app">
            <button style="
                width: 100%;
                padding: 12px;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;">
                🔵 Continue with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ----------------------------
    # 📧 EMAIL LOGIN (SUPABASE AUTH)
    # ----------------------------
    st.markdown("### Or login with Email")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                st.session_state.logged_in = True
                st.session_state.username = response.user.email

                st.success("Login successful ✅")
                st.rerun()

        except Exception as e:
            st.error("Invalid email or password ❌")

    st.markdown("---")

    # ----------------------------
    # 🆕 SIGNUP (SUPABASE AUTH)
    # ----------------------------
    st.markdown("### New user? Sign Up")

    new_email = st.text_input("New Email", key="signup_email")
    new_password = st.text_input("New Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        try:
            response = supabase.auth.sign_up({
                "email": new_email,
                "password": new_password
            })

            st.success("Signup successful 🎉 Please login now")

        except Exception as e:
            st.error("Signup failed ❌")

    st.markdown("---")

    # ----------------------------
    # 🔁 RESET PASSWORD
    # ----------------------------
    st.markdown("### Forgot Password?")

    reset_email = st.text_input("Enter your email", key="reset_email")

    if st.button("Send Reset Link"):
        try:
            supabase.auth.reset_password_email(reset_email)

            st.success("Password reset email sent 📧")

        except Exception as e:
            st.error("Failed to send reset email ❌")