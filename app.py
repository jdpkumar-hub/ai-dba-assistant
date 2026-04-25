import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import pandas as pd

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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "usage" not in st.session_state:
    st.session_state.usage = 0

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
        """)

    with col2:
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
# 💬 CHATGPT STYLE UI
# ===============================
elif page == "AI Chat":

    st.title("🤖 AI DBA Assistant")

    # ---------------------------
    # QUICK BUTTONS
    # ---------------------------
    col1, col2, col3, col4 = st.columns(4)

    if col1.button("🐢 Slow Query"):
        st.session_state.messages.append({"role": "user", "content": "Why is my Oracle query slow?"})

    if col2.button("🔥 High CPU"):
        st.session_state.messages.append({"role": "user", "content": "Oracle high CPU troubleshooting steps"})

    if col3.button("💾 Tablespace Full"):
        st.session_state.messages.append({"role": "user", "content": "Tablespace full issue fix"})

    if col4.button("🔒 Lock Issue"):
        st.session_state.messages.append({"role": "user", "content": "Oracle locking issue troubleshooting"})

    st.divider()

    # ---------------------------
    # DISPLAY CHAT HISTORY
    # ---------------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ---------------------------
    # INPUT BOX (BOTTOM)
    # ---------------------------
    user_input = st.chat_input("Ask your DBA question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # usage limit
        if st.session_state.usage >= 20:
            st.warning("🚫 Free limit reached")
            st.stop()

        st.session_state.usage += 1

        # AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *st.session_state.messages
                    ]
                )

                answer = response.choices[0].message.content
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

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
st.caption("🚀 AI DBA Assistant - ChatGPT Style")