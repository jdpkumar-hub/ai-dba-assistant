import streamlit as st
from supabase import create_client

# ================= CONFIG =================
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlcXVxc2J2aHlkdnVnaWZldmhtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUyNzAzOTUsImV4cCI6MjA5MDg0NjM5NX0.AMTQgSM56qdYy3VOmq9frtBzg_a6TC7c03rp4YgH8cw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-dba-assistant.streamlit.app"


# ================= PASSWORD RECOVERY =================
# ================= PASSWORD RECOVERY =================
#uery_params = st.query_params
#
# query_params.get("type") == "recovery":
#  st.title("🔑 Reset Your Password")
#
#  new_password = st.text_input("New Password", type="password")
#
#  if st.button("Update Password"):
#      try:
#          # 🔥 Try update directly (new SDK)
#          supabase.auth.update_user({
#              "password": new_password
#          })
#
#          st.success("✅ Password updated successfully!")
#          st.query_params.clear()
#
#      except Exception as e:
#          # 🔥 Fallback for old SDK (manual session required)
#          try:
#              access_token = query_params.get("access_token")
#              refresh_token = query_params.get("refresh_token")
#
#              if isinstance(access_token, list):
#                  access_token = access_token[0]
#              if isinstance(refresh_token, list):
#                  refresh_token = refresh_token[0]
#
#              supabase.auth.set_session({
#                  "access_token": access_token,
#                  "refresh_token": refresh_token
#              })
#
#              supabase.auth.update_user({
#                  "password": new_password
#              })
#
#              st.success("✅ Password updated successfully!")
#
#          except Exception as inner_error:
#              st.error("❌ Failed to update password")
#              st.write(inner_error)
#
#  st.stop()
#================================================
def login():
    st.subheader("Login")

    # ================= EMAIL LOGIN =================
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", key="login_btn"):
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
def reset_with_otp():
    st.markdown("## 🔑 Reset Password (OTP)")

    email = st.text_input("Email", key="reset_email")

    if st.button("Send OTP", key="reset_send_otp"):
        try:
            supabase.auth.sign_in_with_otp({
                "email": email
            })
            st.success("📩 OTP sent to your email")

            # store separately
            st.session_state["reset_email_store"] = email

        except Exception as e:
            st.error("Failed to send OTP")
            st.write(e)

    otp = st.text_input("Enter OTP", key="reset_otp")
    new_password = st.text_input("New Password", type="password", key="reset_new_pass")

    if st.button("Verify OTP & Reset", key="reset_verify_btn"):
        try:
            res = supabase.auth.verify_otp({
                "email": st.session_state.get("reset_email_store"),
                "token": otp,
                "type": "email"
            })

            if res.user:
                supabase.auth.update_user({
                    "password": new_password
                })

                st.success("✅ Password updated successfully!")
                st.info("Please login with your new password")

                # ✅ safe cleanup
                st.session_state.pop("reset_email_store", None)

       except Exception as e:
            error_msg = str(e)

            if "New password should be different" in error_msg:
                st.warning("⚠️ New password must be different from old password")
            else:
                st.error("❌ Invalid OTP or failed reset")

            st.write(error_msg)

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