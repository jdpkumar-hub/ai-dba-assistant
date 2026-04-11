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
# 🧑‍💻 LOGIN LANDING PAGE (TABS UI)
# =========================================================
if not user:

    col1, col2 = st.columns([1, 1])

    # -------- LEFT PANEL --------
    with col1:
        st.image("logo.png", width=220)
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

        tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])

        # ---------------- LOGIN TAB ----------------
        with tab1:
            login()   # 👈 YOUR GOOGLE LOGIN (UNCHANGED)

        # ---------------- SIGNUP TAB ----------------
        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pass")

            if st.button("Create Account"):
                try:
                    supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    st.success("✅ Account created! Please login.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # ---------------- RESET TAB ----------------
        with tab3:
            email = st.text_input("Enter your email", key="reset_email")

            if st.button("Send Reset Link"):
                try:
                    supabase.auth.reset_password_email(email)
                    st.success("📧 Reset link sent to your email")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =========================================================
# 🎯 SIDEBAR
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

# =========================================================
# 🧠 MAIN CONTENT
# =========================================================
if page == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.info("Welcome to AI DBA Assistant 🚀")

elif page == "💬 AI Chat":
    st.markdown("## 💬 AI DBA Chat")

    question = st.text_input("Ask Oracle question...")

    if question:
        st.markdown("### 🔍 Analysis")

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

/* LEFT PANEL (brand area) */
.left-panel {
    background: linear-gradient(135deg, #e0ecff, #f0f6ff);
    padding: 40px;
    border-radius: 20px;
    height: 100%;
}

/* RIGHT PANEL (card) */
.card {
    background-color: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08);
}

/* Move right panel slightly left */
.right-panel {
    margin-left: -40px;
}

/* Remove extra padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

elif page == "📊 Reports":
    st.markdown("## 📊 Reports")
    st.info("Reports module coming soon")

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    st.info("Settings panel")