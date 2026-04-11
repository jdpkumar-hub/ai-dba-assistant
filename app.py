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
# 🎨 STYLE
# -------------------------------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #f8fafc;
}
.card {
    background-color: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 🔐 HANDLE OAUTH CODE (DO NOT TOUCH)
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
# 🧑‍💻 LOGIN LANDING PAGE (NEW UI)
# =========================================================
if not user:

    col1, col2 = st.columns([1, 1])

    # -------- LEFT PANEL --------
    with col1:
        st.image("logo.png", width=120)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization Platform")

        st.markdown("""
### Features
- ⚡ SQL Performance Tuning  
- 📊 AWR Analysis  
- 🤖 AI Recommendations  
- 🚀 Real-time Insights  
""")

    # -------- RIGHT PANEL --------
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        option = st.selectbox(
            "Choose Action",
            ["Login", "Create Account", "Reset Password"]
        )

        # ---------------- LOGIN ----------------
        if option == "Login":
            st.subheader("🔐 Login")
            login()   # 👈 YOUR EXISTING GOOGLE LOGIN (UNCHANGED)

        # ---------------- SIGNUP ----------------
        elif option == "Create Account":
            st.subheader("🆕 Create Account")

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Create Account"):
                try:
                    supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    st.success("✅ Account created! Please login.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # ---------------- RESET ----------------
        elif option == "Reset Password":
            st.subheader("🔑 Reset Password")

            email = st.text_input("Enter your email")

            if st.button("Send Reset Link"):
                try:
                    supabase.auth.reset_password_email(email)
                    st.success("📧 Reset link sent to your email")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =========================================================
# 🎯 MAIN APP (UNCHANGED CORE)
# =========================================================
with st.sidebar:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("logo.png", width=60)

    with col2:
        st.markdown("### AI DBA")
        st.caption("Smart Optimization")

    st.divider()

    page = st.radio("", ["🏠 Dashboard", "💬 AI Chat", "📊 Reports", "⚙️ Settings"])

    st.divider()

    st.markdown("### 👤 User")
    st.success(f"{user.email}")

    logout()

# -------------------------------
# MAIN CONTENT
# -------------------------------
if page == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.info("Welcome to AI DBA Assistant 🚀")

elif page == "💬 AI Chat":
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

elif page == "📊 Reports":
    st.markdown("## 📊 Reports")
    st.info("Reports module coming soon")

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    st.info("Settings panel")