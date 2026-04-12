import streamlit as st
from supabase import create_client

# -------------------------------
# 🔑 CONFIG
# -------------------------------
SUPABASE_URL = "https://wequqsbvhydvugifevhm.supabase.co"
SUPABASE_KEY = "sb_publishable_ZOfGu0PLriJqtJLdmk6Bkg_mJ3HrURB"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-oracle-assistant.streamlit.app"

# -------------------------------
# 🔐 LOGIN FUNCTION
# -------------------------------
def login():
    st.markdown("## 🔐 Login")

    # 🔵 Google Login Button
    if st.button("🔵 Continue with Google"):

        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": REDIRECT_URL,
                "query_params": {
                    "prompt": "consent"
                }
            }
        })

        auth_url = res.url

        if auth_url:
            # Fallback clickable link
            st.markdown(f"[👉 Click here if not redirected]({auth_url})")

            # Auto redirect
            st.markdown(
                f"""
                <script>
                window.location.href = "{auth_url}";
                </script>
                """,
                unsafe_allow_html=True
            )

            return False

    # -------------------------------
    # ✅ SESSION HANDLING AFTER REDIRECT
    # -------------------------------
    user = get_user()

    if user:
        # Store session safely
        if "user" not in st.session_state or st.session_state.user is None:
            st.session_state.user = user
            st.rerun()

    return False


# -------------------------------
# 🔐 GET USER (REAL CHECK)
# -------------------------------
def get_user():
    try:
        res = supabase.auth.get_user()
        return res.user if res else None
    except Exception:
        return None


# -------------------------------
# 🚪 LOGOUT
# -------------------------------
def logout():
    if st.button("🚪 Logout"):
        try:
            supabase.auth.sign_out()
        except:
            pass

        # Clear session
        st.session_state.clear()
        st.rerun()