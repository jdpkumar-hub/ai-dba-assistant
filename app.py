import streamlit as st
from auth import login, logout, get_user, supabase

# -------------------------------
# ⚙️ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI DBA Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# 🎨 STYLE (FIXED + CLEAN)
# -------------------------------
st.markdown("""
<style>

/* App background */
.main {
    background-color: #f3f6fb;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f8fafc;
}

/* LEFT PANEL */
.left-panel {
    background: linear-gradient(135deg, #e0ecff, #f0f6ff);
    padding: 40px;
    border-radius: 20px;
}

/* RIGHT PANEL */
.card {
    background-color: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08);
}

/* Shift right panel slightly left */
.right-panel {
    margin-left: -30px;
}

/* Spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🔐 HANDLE OAUTH CODE
# -------------------------------
params = st.query_params

if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({"auth_code": params["code"]})
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

# -------------------------------
# 🔐 CHECK USER
# -------------------------------
user = get_user()

# =========================================================
# 🧑‍💻 LOGIN PAGE
# =========================================================
if not user:

    col1, col2, col3 = st.columns([1.2, 1, 0.3])

    # -------- LEFT PANEL --------
    with col1:
        st.markdown('<div class="left-panel">', unsafe_allow_html=True)

        st.image("logo.png", width=120)
       