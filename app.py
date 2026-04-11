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
# 🎨 GLOBAL STYLE
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
    height: 100%;
}

/* RIGHT PANEL */
.card {
    background-color: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.08);
}

/* Move login slightly left */
.right-panel {
    margin-left: -30px;
}

/* spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ----------------