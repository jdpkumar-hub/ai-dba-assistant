import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import pandas as pd
from bs4 import BeautifulSoup

# ===============================
# CONFIG
# ===============================
st.set_page_config(
    page_title="AI DBA Assistant",
    page_icon="🤖",
    layout="wide"
)

# ===============================
# LOAD CSS
# ===============================
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()

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
# 🧠 USER PLAN FUNCTIONS
# ===============================
def ensure_user_plan(user):
    try:
        if not user or not user.email:
            return

        res = supabase.table("user_plans")\
            .select("*")\
            .eq("email", user.email)\
            .execute()

        if not res.data:
            supabase.table("user_plans").insert({
                "email": user.email,
                "plan": "free",
                "usage_count": 0
            }).execute()

    except Exception as e:
        st.error(f"ensure_user_plan error: {e}")

def get_user_plan(user):
    try:
        res = supabase.table("user_plans")\
            .select("*")\
            .eq("email", user.email)\
            .execute()

        if not res.data:
            return {"plan": "free", "usage_count": 0}

        return res.data[0]

    except Exception as e:
        st.error(f"get_user_plan error: {e}")
        return {"plan": "free", "usage_count": 0}

def check_usage(user):
    data = get_user_plan(user)

    if data["plan"] == "free" and data["usage_count"] >= 20:
        st.warning("🚫 Free limit reached. Upgrade required.")
        st.stop()

def increment_usage(user):
    try:
        data = get_user_plan(user)
        count = data["usage_count"]

        supabase.table("user_plans").update({
            "usage_count": count + 1
        }).eq("email", user.email).execute()

    except Exception as e:
        st.error(f"increment_usage error: {e}")

# ===============================
# 🧠 AWR HTML PARSER
# ===============================
def parse_awr_html(content):
    try:
        soup = BeautifulSoup(content, "lxml")
        text = soup.get_text(separator="\n")

        sections = {
            "load_profile": "",
            "wait_events": "",
            "top_sql": ""
        }

        lines = text.split("\n")

        for i, line in enumerate(lines):
            if "Load Profile" in line:
                sections["load_profile"] = "\n".join(lines[i:i+40])

            if "Top 10 Foreground Events" in line:
                sections["wait_events"] = "\n".join(lines[i:i+40])

            if "SQL ordered by Elapsed Time" in line:
                sections["top_sql"] = "\n".join(lines[i:i+60])

        return sections

    except Exception as e:
        return {"error": str(e)}

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
    col1, col2 = st.columns([1.4, 0.8])

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
        tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Reset"])
        with tab1: login()
        with tab2: signup()
        with tab3: reset_password()

    st.stop()

# ===============================
# ENSURE USER PLAN
# ===============================
ensure_user_plan(user)
plan_data = get_user_plan(user)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("image/logo2.png", width=200)
    page = st.radio("", ["AI Chat", "Dashboard", "History"])

    st.success(user.email)
    st.info(f"Plan: {plan_data['plan']} | Usage: {plan_data['usage_count']}")

    if plan_data["plan"] == "free":
        st.warning("Upgrade to Pro 🚀")

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
        df["created_at"] = pd.to_datetime(df["created_at"])
        st.line_chart(df.groupby(df["created_at"].dt.date).size())

# ===============================
# AI CHAT
# ===============================
elif page == "AI Chat":

    st.title("🤖 AI DBA Assistant")

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    # ================= CHAT =================
    with tab1:

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

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Ask your DBA question...")

        if user_input:
            check_usage(user)

            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

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
            increment_usage(user)

    # ================= SQL =================
    with tab2:

        st.subheader("⚡ SQL Performance Analyzer")
        sql = st.text_area("Paste your SQL query")

        if st.button("🚀 Analyze SQL"):
            if sql:
                check_usage(user)

                with st.spinner("Analyzing SQL..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"""
Analyze this Oracle SQL:

{sql}

Provide:
- Issues
- Execution Plan Advice
- Index Suggestions
- Optimized Query
"""}
                        ]
                    )

                    st.success("Analysis Complete")
                    st.write(response.choices[0].message.content)

                increment_usage(user)

    # ================= AWR =================
    with tab3:

        st.subheader("📊 AWR Report Analyzer")

        file = st.file_uploader("Upload AWR report (.txt / .html)", type=["txt", "html"])

        if file:
            raw_content = file.read()

            if file.name.endswith(".html"):
                parsed = parse_awr_html(raw_content.decode(errors="ignore"))

                structured_content = f"""
LOAD PROFILE:
{parsed.get("load_profile")}

WAIT EVENTS:
{parsed.get("wait_events")}

TOP SQL:
{parsed.get("top_sql")}
"""
            else:
                structured_content = raw_content.decode(errors="ignore")

            if st.button("🚀 Analyze AWR"):
                check_usage(user)

                with st.spinner("Analyzing AWR..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"""
Analyze this Oracle AWR report:

{structured_content}

Provide:
- Top Bottlenecks
- Wait Events
- CPU vs IO
- Problematic SQL
- Recommendations
"""}
                        ]
                    )

                    result = response.choices[0].message.content

                    st.success("AWR Analysis Complete")
                    st.write(result)

                    # SAVE TO DB
                    try:
                        supabase.table("awr_reports").insert({
                            "user_email": user.email,
                            "file_name": file.name,
                            "analysis": result
                        }).execute()
                    except Exception as e:
                        st.error(f"DB Save Error: {e}")

                increment_usage(user)

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

    st.subheader("📊 AWR Reports")

    awr_data = supabase.table("awr_reports")\
        .select("*")\
        .eq("user_email", user.email)\
        .execute()

    awr_df = pd.DataFrame(awr_data.data)

    if not awr_df.empty:
        st.dataframe(awr_df[["file_name", "created_at"]])

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("🚀 AI DBA Assistant | JDP | SaaS Ready")
```
