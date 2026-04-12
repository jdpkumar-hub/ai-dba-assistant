import streamlit as st
from auth import login, logout, get_user, supabase
import os
from openai import OpenAI
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from auth import login, signup, reset_password, logout, get_user, supabase
#-----------------------------------------------------
# DOWNLOAD REPORT
#-----------------------------------------------------

def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    story = []

    # Split into lines
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if not line:
            story.append(Spacer(1, 10))
            continue

        # Headings
        if line.startswith("###") or line.startswith("##"):
            story.append(Paragraph(f"<b>{line.replace('#','').strip()}</b>", styles["Heading2"]))
        else:
            story.append(Paragraph(line, styles["Normal"]))

        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)

    return buffer

# -------------------------------
# 🔐 HANDLE OAUTH CALLBACK (FIXED)
# -------------------------------
params = st.query_params

# 🔑 PASSWORD RESET HANDLER (FIRST)
if "type" in params and params["type"] == "recovery":
    st.session_state.reset_mode = True
    st.query_params.clear()
    st.rerun()

# 🔐 OAUTH HANDLER
if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })

        st.query_params.clear()

        user = get_user()
        if user and "user" not in st.session_state:
        st.session_state.user = user
        st.rerun()
 

    except Exception as e:
        st.error(f"Login failed: {e}")
        
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#-----------------------------------------------------
# DOWNLOAD REPORT
#-----------------------------------------------------
#def create_pdf(text):
#   buffer = BytesIO()
#
#   doc = SimpleDocTemplate(buffer)
#   styles = getSampleStyleSheet()
#   story = [Paragraph(text, styles["Normal"])]
#   doc.build(story)
#
#   buffer.seek(0)
#   return buffer

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
# USER CHECK (FIXED)
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

user = get_user()

if user:
    st.session_state.user = user

user = st.session_state.user

# ================= LOGIN =================
if not user:

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("image/logo2.png", width=220)
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
        signup()

    with tab3:
        reset_password()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ================= MAIN =================
with st.sidebar:
    st.image("image/logo2.png", width=220)
    page = st.radio("", ["🏠 Dashboard", "💬 AI Chat", "📊 Reports", "📜 History", "⚙️ Settings"])
    st.success(user.email)
    logout()

# ================= PAGES =================
if page == "🏠 Dashboard":
    st.title("📊 Dashboard")

    try:
        data = supabase.table("query_history")\
            .select("*")\
            .eq("user_email", user.email)\
            .execute()

        df = pd.DataFrame(data.data)

        if not df.empty:

            # METRICS
            col1, col2 = st.columns(2)

            col1.metric("Total Queries", len(df))

            df["created_at"] = pd.to_datetime(df["created_at"])
            df["date"] = df["created_at"].dt.date

            col2.metric("Active Days", df["date"].nunique())

            st.divider()

            # 📈 LINE CHART
            st.subheader("📈 Queries Trend")
            trend = df.groupby("date").size()
            st.line_chart(trend)

            st.divider()

            # 📊 TYPE BREAKDOWN
            def classify(q):
                if "AWR" in q:
                    return "AWR"
                elif "select" in q.lower():
                    return "SQL"
                else:
                    return "Chat"

            df["type"] = df["question"].apply(classify)
            type_count = df["type"].value_counts()

            st.subheader("📊 Usage Breakdown")
            st.bar_chart(type_count)

        else:
            st.info("No data yet")

    except Exception as e:
        st.error("Error loading dashboard")

elif page == "💬 AI Chat":
    st.title("AI DBA Assistant")

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    # CHAT
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
                answer = response.choices[0].message.content
                st.write(answer)

                # ✅ FIXED INDENTATION
                pdf_file = create_pdf(answer)
                st.download_button(
                    "📄 Download Report",
                    pdf_file,
                    file_name="report.pdf"
                    )

                try:
                    supabase.table("query_history").insert({
                        "user_email": user.email,
                        "question": question,
                        "response": answer
                    }).execute()
                except:
                    st.warning("History not saved")

    # SQL
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
                    answer = response.choices[0].message.content
                    st.write(answer)

                    # ✅ FIXED INDENTATION
                    pdf_file = create_pdf(answer)
                    st.download_button(
                        "📄 Download Report",
                        pdf_file,
                        file_name="report.pdf"
                     )

                    try:
                        supabase.table("query_history").insert({
                            "user_email": user.email,
                            "question": sql,
                            "response": answer
                        }).execute()
                    except:
                        st.warning("History not saved")

    # AWR (unchanged)
    with tab3:
        st.markdown("### 📊 AWR Report Analyzer")

        uploaded_file = st.file_uploader("Upload AWR report (.txt)", type=["txt"])

        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")

            if st.button("Analyze AWR"):
                with st.spinner("Analyzing AWR Report..."):
                    try:
                        prompt = f"""Analyze this Oracle AWR report:
{content[:15000]}"""

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Oracle performance expert"},
                                {"role": "user", "content": prompt}
                            ]
                        )

                        result = response.choices[0].message.content
                        st.write(result)

                        try:
                            supabase.table("query_history").insert({
                                "user_email": user.email,
                                "question": "AWR Report",
                                "response": result
                            }).execute()
                        except:
                            st.warning("History not saved")

                    except Exception as e:
                        st.error(f"AWR Error: {e}")

elif page == "📜 History":
    st.title("📜 Query History")

    search = st.text_input("🔍 Search")

    data = supabase.table("query_history")\
        .select("*")\
        .eq("user_email", user.email)\
        .order("created_at", desc=True)\
        .execute()

    results = data.data

    if search:
        results = [r for r in results if search.lower() in r["question"].lower()]

    for row in results:
        with st.expander(f"🧠 {row['question'][:50]}"):
            st.markdown(f"**Answer:** {row['response']}")

elif page == "📊 Reports":
    st.title("Reports")

elif page == "⚙️ Settings":
    st.title("Settings")