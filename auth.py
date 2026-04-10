import streamlit as st
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------------
# 🔐 HANDLE LOGIN RESPONSE
# -------------------------------
def handle_auth():
    query_params = st.query_params

    if "access_token" in query_params:
        st.session_state["logged_in"] = True
        st.session_state["access_token"] = query_params["access_token"]

        # Clean URL (PRO UX 🔥)
        st.query_params.clear()

        st.success("✅ Login successful!")
        st.rerun()


# -------------------------------
# 🔗 GOOGLE LOGIN URL
# -------------------------------
def google_login():
    try:
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "https://ai-oracle-assistant.streamlit.app"
            }
        })

        return res.url

    except Exception as e:
        st.error(f"Login error: {e}")
        return None


# -------------------------------
# 🎨 LOGIN UI
# -------------------------------
def login():
    st.title("🔐 Login")

    handle_auth()  # 👈 VERY IMPORTANT

    if st.session_state.get("logged_in"):
        return True

    st.markdown("### Continue with Google")

    if st.button("🔵 Continue with Google"):
        url = google_login()

        if url:
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={url}">',
                unsafe_allow_html=True
            )

    return False


# -------------------------------
# 🚪 LOGOUT
# -------------------------------
def logout():
    st.session_state.clear()
    st.rerun()