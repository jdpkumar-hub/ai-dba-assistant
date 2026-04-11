import streamlit as st
from supabase import create_client

# -------------------------------
# 🔑 CONFIG
# -------------------------------
SUPABASE_URL = "https://wequqsbvhdyvugifevhm.supabase.co"
SUPABASE_KEY = "sb_publishable_ZOfGu0PLriJqtJLdmk6Bkg_mJ3HrURB"   # 👈 put your key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

REDIRECT_URL = "https://ai-oracle-assistant.streamlit.app"

# -------------------------------
# 🔐 LOGIN FUNCTION
# -------------------------------
def login():
    st.markdown("## 🔐 Login")

    if st.button("🔵 Continue with Google"):

        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": REDIRECT_URL,
                "query_params": {
                    "prompt": "consent"  # 👈 always show Google screen
                }
            }
        })

        auth_url = res.get("url")

        if auth_url:
            st.markdown(f"[👉 Click here if not redirected]({auth_url})")
            st.markdown(
                f"""
                <script>
                window.location.href = "{auth_url}";
                </script>
                """,
                unsafe_allow_html=True
            )
            return False

    return False


# -------------------------------
# 🔐 GET USER (REAL CHECK)
# -------------------------------
def get_user():
    try:
        res = supabase.auth.get_user()
        return res.user if res else None
    except:
        return None


# -------------------------------
# 🚪 LOGOUT
# -------------------------------
def logout():
    if st.button("🚪 Logout"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()