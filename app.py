import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
import os
from openai import OpenAI
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime

# ===============================
# 🔐 SESSION INIT
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None

if "history" not in st.session_state:
    st.session_state.history = []

if "usage" not in st.session_state:
    st.session_state.usage = 0

# ===============================
# 🧠 SYSTEM PROMPT (DBA EXPERT)
# ===============================
SYSTEM_PROMPT = """
You are a Senior Oracle DBA with 20+ years experience.

Always provide:
- Root Cause
- Diagnostic Queries
- Fix Steps
- Risks
- Best Practices

Be precise and production-ready.
"""

# ===============================
# 👑 ADMIN
# ===============================
ADMIN_EMAIL = "aidbaassistant@gmail.com"

def is_admin(user):
    return user and user.email == ADMIN_EMAIL

# ===============================
# 🔐 OPENAI
# ===============================
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing OPENAI_API_KEY")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ===============================
# 📄 PDF GENERATOR
# ===============================
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ===============================
# ⚡ USAGE LIMIT
# ===============================
def check_usage():
    if st.session_state.usage >= 20:
        st.warning("🚫 Free limit reached. Upgrade required.")
        st.stop()
    st.session_state.usage += 1

# ===============================
# 💾 SAVE HISTORY
# ===============================
def save_history(question, answer, user):
    try:
        supabase.table("query_history").insert({
            "user_email": user.email,
            "question": question,
            "answer": answer,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except:
        pass

# ===============================
# ⚡ STREAMING OUTPUT
# ===============================
def stream_response(prompt):
    placeholder = st.empty()
    full_text = ""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt
    )

    text = response.choices[0].message.content

    for word in text.split():
        full_text += word + " "
        placeholder.markdown(full_text)

    return text

# ===============================
# 🔐 AUTH
# ===============================
user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

# ===============================
# LOGIN PAGE
# ===============================
if not user:
    st.title("🚀 AI DBA Assistant")

    tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Reset"])
    with tab1: login()
    with tab2: signup()
    with tab3: reset_password()

    st.stop()

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.title("AI DBA")
    page = st.radio("", ["Dashboard", "AI Chat", "History", "Settings"])
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

    # Prompt shortcuts
    col1, col2, col3 = st.columns(3)

    if col1.button("🐢 Slow Query"):
        st.session_state.quick = "Why is my query slow in Oracle?"

    if col2.button("🔥 High CPU"):
        st.session_state.quick = "Oracle high CPU troubleshooting"

    if col3.button("💾 Tablespace Full"):
        st.session_state.quick = "Tablespace full fix"

    mode = st.selectbox("Mode", ["Chat", "SQL Analyzer", "AWR Analyzer"])

    # ================= CHAT =================
    if mode == "Chat":
        question = st.text_input("Ask DBA question", value=st.session_state.get("quick",""))

        if question:
            check_usage()

            prompt = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]

            answer = stream_response(prompt)

            save_history(question, answer, user)

            pdf = create_pdf(answer)
            st.download_button("📄 Download", pdf, "report.pdf")

    # ================= SQL =================
    elif mode == "SQL Analyzer":
        sql = st.text_area("Paste SQL")

        if st.button("Analyze SQL"):
            check_usage()

            prompt = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
Analyze this Oracle SQL:

{sql}

Give:
- Execution Plan Advice
- Index Suggestions
- Optimized Query
"""}
            ]

            answer = stream_response(prompt)

            save_history(sql, answer, user)

    # ================= AWR =================
    elif mode == "AWR Analyzer":
        file = st.file_uploader("Upload AWR", type=["txt"])

        if file:
            content = file.read().decode()[:15000]

            if st.button("Analyze AWR"):
                check_usage()

                prompt = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"""
Analyze AWR:

{content}

Find:
- Bottlenecks
- Wait Events
- Fix Recommendations
"""}
                ]

                answer = stream_response(prompt)

                save_history("AWR Report", answer, user)

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
# SETTINGS
# ===============================
elif page == "Settings":
    st.title("⚙️ Settings")

    if st.button("Reset Usage"):
        st.session_state.usage = 0
        st.success("Reset done")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("🚀 AI DBA Assistant - Production Ready")