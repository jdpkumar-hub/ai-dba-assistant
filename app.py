import streamlit as st
from auth import login, logout, get_user, supabase
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.card {
    background-color: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08);
}

.right-panel {
    margin-top: 40px;
}

.feature {
    padding: 12px;
    border-radius: 12px;
    transition: 0.3s;
}
.feature:hover {
    background-color: #f5f7ff;
    transform: translateX(3px);
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
# 🔐 LOGIN PAGE
# =========================================================
if not user:

    col1, col2 = st.columns([1, 3])

    # LEFT PANEL
    with col1:
        st.image("logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization Platform")

        st.markdown("""
<div class="feature">⚡ <b>SQL Performance Tuning</b><br><small>Optimize slow queries</small></div>
<div class="feature">📊 <b>AWR Analysis</b><br><small>Analyze workload reports</small></div>
<div class="feature">🤖 <b>AI Recommendations</b><br><small>Smart tuning suggestions</small></div>
<div class="feature">🚀 <b>Real-time Insights</b><br><small>Live monitoring</small></div>
""", unsafe_allow_html=True)

    # RIGHT PANEL
    with col2:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])

        with tab1:
            login()

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

        with tab3:
            email = st.text_input("Enter your email", key="reset_email")

            if st.button("Send Reset Link"):
                try:
                    supabase.auth.reset_password_email(email)
                    st.success("📧 Reset link sent")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =========================================================
# 🎯 MAIN APP
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
    st.success(user.email)

    logout()

# -------------------------------
# MAIN CONTENT
# -------------------------------

if page == "🏠 Dashboard":
    st.markdown("## 🏠 Dashboard")
    st.info("Welcome to AI DBA Assistant 🚀")

#elif page == "💬 AI Chat":
#    st.markdown("## 💬 AI DBA Chat")
#
#    question = st.text_input("Ask Oracle question...")
#
#    if question:
#        with st.spinner("Analyzing..."):
#            try:
#                response = client.chat.completions.create(
#                    model="gpt-4o-mini",
#                    messages=[
#                        {"role": "system", "content": "You are an Oracle DBA expert."},
#                        {"role": "user", "content": question}
#                    ]
#                )
#
#                answer = response.choices[0].message.content
#
#                st.markdown("### 🤖 AI Response")
#                st.write(answer)
#
#            except Exception as e:
#                st.error(f"AI Error: {e}")
#===============================================
#AI CHAT START
#===============================================
elif page == "💬 AI Chat":
    st.markdown("## 💬 AI DBA Assistant")

    tab1, tab2 = st.tabs(["💬 Ask AI", "⚡ SQL Analyzer"])

    # =========================
    # 💬 CHAT TAB
    # =========================
    with tab1:
        question = st.text_input("Ask Oracle DBA question...")

        if question:
            with st.spinner("Analyzing..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert Oracle DBA helping with performance tuning."},
                            {"role": "user", "content": question}
                        ]
                    )

                    answer = response.choices[0].message.content

                    st.markdown("### 🤖 AI Response")
                    st.write(answer)

                except Exception as e:
                    st.error(f"AI Error: {e}")

    # =========================
    # ⚡ SQL ANALYZER TAB
    # =========================
    with tab2:
        st.markdown("### ⚡ SQL Performance Analyzer")

        sql_query = st.text_area("Paste your SQL query here", height=150)

        if st.button("Analyze SQL"):
            if sql_query:
                with st.spinner("Analyzing SQL..."):
                    try:
                        prompt = f"""
Analyze this Oracle SQL query and provide:

1. Issues in query
2. Performance problems
3. Index suggestions
4. Optimized query rewrite

SQL:
{sql_query}
"""

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You are an Oracle SQL tuning expert."},
                                {"role": "user", "content": prompt}
                            ]
                        )

                        result = response.choices[0].message.content

                        st.markdown("## 🔍 SQL Analysis Report")
                        st.write(result)

                    except Exception as e:
                        st.error(f"AI Error: {e}")

#===============================================
#AI CHAT END
#===============================================
elif page == "📊 Reports":
    st.markdown("## 📊 Reports")
    st.info("Reports module coming soon")

elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")
    st.info("Settings panel")