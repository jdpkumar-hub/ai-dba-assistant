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
.block-container { padding-top: 1rem; }

.card {
    background-color: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08);
}

.right-panel { margin-top: 40px; }

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
# 🔐 HANDLE OAUTH
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
# USER CHECK
# -------------------------------
user = get_user()

# ================= LOGIN =================
if not user:

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization Platform")

        st.markdown("""
<div class="feature">⚡ SQL Performance Tuning</div>
<div class="feature">📊 AWR Analysis</div>
<div class="feature">🤖 AI Recommendations</div>
<div class="feature">🚀 Real-time Insights</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])

        with tab1:
            login()

        with tab2:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Create Account"):
                try:
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Account created")
                except Exception as e:
                    st.error(e)

        with tab3:
            email = st.text_input("Reset Email")

            if st.button("Send Reset"):
                try:
                    supabase.auth.reset_password_email(email)
                    st.success("Email sent")
                except Exception as e:
                    st.error(e)

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ================= MAIN =================
with st.sidebar:
    st.image("logo.png", width=60)
    page = st.radio("", ["🏠 Dashboard", "💬 AI Chat", "📊 Reports", "⚙️ Settings"])
    st.success(user.email)
    logout()

# ================= PAGES =================
if page == "🏠 Dashboard":
    st.title("Dashboard")

elif page == "💬 AI Chat":
    st.title("AI DBA Assistant")

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    # ---------------- CHAT ----------------
    with tab1:
        question = st.text_input("Ask anything...")

        if question:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Oracle DBA expert"},
                        {"role": "user", "content": question}
                    ]
                )
                st.write(response.choices[0].message.content)

    # ---------------- SQL ANALYZER ----------------
    with tab2:
        sql = st.text_area("Paste SQL")

        if st.button("Analyze"):
            if sql:
                with st.spinner("Analyzing..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "SQL tuning expert"},
                            {"role": "user", "content": sql}
                        ]
                    )
                    st.write(response.choices[0].message.content)

    # ---------------- AWR ANALYZER (FIXED) ----------------
    with tab3:
        st.markdown("### 📊 AWR Report Analyzer")

        uploaded_file = st.file_uploader("Upload AWR report (.txt)", type=["txt"])

        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")

            if st.button("Analyze AWR"):
                with st.spinner("Analyzing AWR Report..."):
                    try:
                        prompt = f"""
Analyze this Oracle AWR report and provide:

1. Top performance issues
2. CPU / IO bottlenecks
3. Slow SQL insights
4. Recommendations

AWR Report:
{content[:15000]}
"""

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You are an Oracle performance expert analyzing AWR reports."},
                                {"role": "user", "content": prompt}
                            ]
                        )

                        result = response.choices[0].message.content

                        st.markdown("## 📊 AWR Analysis Report")
                        st.write(result)

                    except Exception as e:
                        st.error(f"AWR Error: {e}")

# ---------------- OTHER PAGES ----------------
elif page == "📊 Reports":
    st.title("Reports")

elif page == "⚙️ Settings":
    st.title("Settings")