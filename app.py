import streamlit as st
from auth import login, logout

# -------------------------------
# ⚙️ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI DBA Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# 🔐 HANDLE TOKEN FROM URL (FIX LOOP)
# -------------------------------
params = st.query_params

if "token" in params:
    st.session_state["logged_in"] = True
    st.session_state["token"] = params["token"]

    # clean URL
    st.query_params.clear()
    st.rerun()

# -------------------------------
# 🔐 AUTH CHECK
# -------------------------------
if not st.session_state.get("logged_in"):
    if not login():
        st.stop()

# -------------------------------
# 🎨 CUSTOM UI
# -------------------------------
st.markdown("""
<style>
.main-title {
    font-size: 28px;
    font-weight: bold;
}
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🧭 SIDEBAR (LEFT PANEL)
# -------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)

    st.markdown("## AI DBA Assistant")
    st.caption("Smart Oracle Optimization")

    st.divider()

    menu = st.radio(
        "Navigation",
        ["🏠 Dashboard", "💬 AI Chat", "📊 Reports", "⚙️ Settings"]
    )

    st.divider()

    st.markdown("### 👤 User")
    st.success("Logged in")

    if st.button("🚪 Logout"):
        logout()

# -------------------------------
# 🏠 MAIN PANEL (RIGHT SIDE)
# -------------------------------
if menu == "🏠 Dashboard":
    st.markdown('<div class="main-title">🚀 Dashboard</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card">⚡ SQL Tuning</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">📊 Performance</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card">🤖 AI Insights</div>', unsafe_allow_html=True)

# -------------------------------
# 💬 CHAT PAGE
# -------------------------------
elif menu == "💬 AI Chat":
    st.markdown("### 💬 AI DBA Chat")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Ask database question...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))

        response = f"""
🔍 **Analysis**

Possible issues:
- Missing indexes
- Full table scans
- High CPU usage

💡 **Suggestion**
- Add index
- Gather stats
- Optimize query
"""

        st.session_state.chat_history.append(("ai", response))

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.chat_message("user").write(msg)
        else:
            st.chat_message("assistant").write(msg)

# -------------------------------
# 📊 REPORTS
# -------------------------------
elif menu == "📊 Reports":
    st.markdown("### 📊 Performance Reports")
    st.info("Coming soon...")

# -------------------------------
# ⚙️ SETTINGS
# -------------------------------
elif menu == "⚙️ Settings":
    st.markdown("### ⚙️ Settings")
    st.info("Manage preferences here")