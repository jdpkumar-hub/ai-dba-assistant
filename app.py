import streamlit as st
from auth import login, logout, get_user

# -------------------------------
# ⚙️ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI DBA Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# 🎨 CUSTOM STYLE
# -------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🔐 AUTH CHECK (CORRECT WAY)
# -------------------------------
user = get_user()

if not user:
    login()
    st.stop()

# -------------------------------
# 🎯 SIDEBAR (LEFT PANEL)
# -------------------------------
with st.sidebar:
    col1, col2 = st.columns([1,2])

    with col1:
        st.image("logo.png", width=60)  # 👈 your logo

    with col2:
        st.markdown("### AI DBA")
        st.caption("Smart Optimization")

    st.divider()

    st.markdown("### Navigation")
    page = st.radio("", ["🏠 Dashboard", "💬 AI Chat", "📊 Reports", "⚙️ Settings"])

    st.divider()

    st.markdown("### 👤 User")
    st.success(f"Logged in as {user.email}")

    logout()

# -------------------------------
# 🧠 MAIN CONTENT
# -------------------------------
if page == "💬 AI Chat":

    st.markdown("## 💬 AI DBA Chat")

    question = st.text_input("Ask Oracle question...")

    if question:
        st.markdown("### 🔍 Analysis")

        st.markdown("""
**Possible issues:**
- Missing indexes  
- Full table scans  
- High CPU usage  

💡 **Suggestion**
- Add index  
- Gather stats  
- Optimize query  
""")

elif page == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.info("Welcome to AI DBA Assistant 🚀")

elif page == "📊 Reports":
    st.markdown("## 📊 Reports")
    st.info("Reports module coming soon")

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    st.info("Settings panel")