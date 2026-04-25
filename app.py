import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

# ===============================
# 🔐 OAUTH CALLBACK
# ===============================
params = st.query_params
if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

# ===============================
# SESSION INIT
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None

if "usage" not in st.session_state:
    st.session_state.usage = 0

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = ""

# ===============================
# OPENAI
# ===============================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OPENAI_API_KEY")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ===============================
# SYSTEM PROMPT
# ===============================
SYSTEM_PROMPT = """
You are a Senior Oracle DBA with 20+ years experience.

Always provide:
- Root Cause
- Diagnostic Queries
- Fix Steps
- Risks
- Best Practices
"""

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# ===============================
# USER SESSION
# ===============================
user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

# ===============================
# LOGIN UI
# ===============================
if not user:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image("image/logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization")

        st.markdown("""
        ⚡ SQL Tuning  
        📊 AWR Analysis  
        🤖 AI Insights  
        🚀 Performance Fixes  
        """)

    with col2:
        st.markdown("### Login")
        tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Reset"])
        with tab1: login()
        with tab2: signup()
        with tab3: reset_password()

    st.stop()

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("image/logo2.png", width=200)
    page = st.radio("", ["Dashboard", "AI Chat", "History"])
    st.success(user.email)
    logout()

# ===============================
# DASHBOARD
# ===============================
if page == "Dashboard":
    st.title("📊 Dashboard")

    data = supabase.table("query_history")\
        .select("*")\
        .eq("user_email", user.email)\
        .execute()

    df = pd.DataFrame(data.data)

    if not df.empty:
        st.metric("Total Queries", len(df))
        st.line_chart(df)

# ===============================
# AI CHAT
# ===============================
elif page == "AI Chat":

    st.title("🤖 AI DBA Assistant")

    # ---------------------------
    # 🔥 CHAT SHORTCUT BUTTONS
    # ---------------------------
    st.subheader("⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("🐢 Slow Query"):
        st.session_state.quick_prompt = "Why is my Oracle query slow? Provide tuning steps."

    if col2.button("🔥 High CPU"):
        st.session_state.quick_prompt = "Oracle database high CPU troubleshooting steps."

    if col3.button("💾 Tablespace Full"):
        st.session_state.quick_prompt = "Tablespace full issue resolution steps."

    if col4.button("🔒 Lock Issue"):
        st.session_state.quick_prompt = "How to identify and fix Oracle locking issues."

    # ---------------------------
    # MODE SELECT
    # ---------------------------
    mode = st.selectbox("Mode", ["Chat", "SQL Analyzer", "AWR Analyzer"])

    # ---------------------------
    # COMMON FUNCTION
    # ---------------------------
    def run_ai(prompt_text):
        if st.session_state.usage >= 20:
            st.warning("🚫 Free limit reached")
            st.stop()

        st.session_state.usage += 1

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_text}
            ]
        )

        return response.choices[0].message.content

    # ================= CHAT =================
    if mode == "Chat":
        question = st.text_input(
            "Ask DBA question",
            value=st.session_state.quick_prompt
        )

        if question:
            answer = run_ai(question)
            st.write(answer)

    # ================= SQL =================
    elif mode == "SQL Analyzer":
        sql = st.text_area("Paste SQL")

        if st.button("Analyze SQL"):
            answer = run_ai(f"Analyze Oracle SQL:\n{sql}")
            st.write(answer)

    # ================= AWR =================
    elif mode == "AWR Analyzer":
        file = st.file_uploader("Upload AWR", type=["txt"])

        if file:
            content = file.read().decode()[:15000]

            if st.button("Analyze AWR"):
                answer = run_ai(content)
                st.write(answer)

# ===============================
# HISTORY
# ===============================
elif page == "History":
    st.title("📜 History")

    data = supabase.table("query_history")\
        .select("*")\
        .eq("user_email", user.email)\
        .execute()

    df = pd.DataFrame(data.data)

    if not df.empty:
        st.dataframe(df)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("🚀 AI DBA Assistant")