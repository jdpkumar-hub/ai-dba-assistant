import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
from bs4 import BeautifulSoup
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from ui_styles import apply_ui_styles, render_centered_title, sidebar_logo
from awr_parser import parse_html, extract_metrics, classify_bottleneck, build_awr_prompt, calculate_health_score
from pdf_generator import generate_awr_pdf, generate_cpu_io_chart

# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")
apply_ui_styles()
render_centered_title()

# ================= CSS =================
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()

# ================= OAUTH =================
params = st.query_params
if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({"auth_code": params["code"]})
        st.query_params.clear()
        st.session_state.user = supabase.auth.get_session().user
        st.rerun()
    except Exception as e:
        st.error(f"OAuth Error: {e}")

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

# ================= LOGIN =================
if not user:
    col1, col2 = st.columns([0.8, 2.0])

    with col1:
        st.image("image/logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization")

    with col2:
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])
        with tab1: login()
        with tab2: signup()
        with tab3: reset_password()

    st.stop()

# ================= OPENAI =================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are a Senior Oracle DBA.
Provide:
- Root Cause
- Fix
- Risks
- Best Practices
"""

# ================= SIMPLE PDF =================
def generate_pdf(text, title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(title, styles["Title"]))
    content.append(Spacer(1, 10))

    for line in text.split("\n"):
        if line.strip():
            content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ================= SIDEBAR =================
with st.sidebar:
    sidebar_logo()
    page = st.radio("", ["AI Chat", "Dashboard", "History"])
    st.success(user.email)
    logout()

# ================= MAIN =================
if page == "AI Chat":

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    # -------- CHAT --------
    with tab1:
        prompt = st.chat_input("Ask...")
        if prompt:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(res.choices[0].message.content)

    # -------- SQL --------
    with tab2:
        sql = st.text_area("Enter SQL")

        if st.button("Analyze SQL"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sql}]
            )

            result = res.choices[0].message.content
            st.write(result)

            pdf = generate_pdf(result, "SQL Report")

            st.download_button(
                "📄 Download SQL Report",
                pdf,
                file_name="sql_report.pdf",
                mime="application/pdf"
            )

    # -------- AWR --------
    with tab3:
        st.subheader("📊 AWR Analyzer")

        file = st.file_uploader("Upload AWR (.txt / .html)", ["txt", "html"])

        if file and st.button("Analyze AWR"):

            content = file.read().decode(errors="ignore")

            if file.name.endswith(".html"):
                content = parse_html(content)

            metrics = extract_metrics(content)
            bottleneck = classify_bottleneck(metrics)

            st.info(f"Detected Bottleneck: {bottleneck}")

            score, level = calculate_health_score(metrics, bottleneck)
            st.metric("Health Score", f"{score} ({level})")

            prompt = build_awr_prompt(metrics)

            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            result = res.choices[0].message.content
            st.write(result)

            # ✅ prevent duplicate insert
            if "saved_awr" not in st.session_state:
                supabase.table("awr_reports").insert({
                    "user_email": user.email,
                    "metrics": metrics,
                    "bottleneck": bottleneck,
                    "score": score,
                    "level": level,
                    "result": result
                }).execute()

                st.session_state.saved_awr = True

            pdf = generate_awr_pdf(result, metrics, score, level)

            st.download_button(
                "📄 Download AWR Report",
                pdf,
                file_name="awr_report.pdf",
                mime="application/pdf"
            )

# ================= DASHBOARD =================
if page == "Dashboard":

    st.title("📊 DBA Dashboard")

    data = supabase.table("awr_reports")\
        .select("*")\
        .eq("user_email", user.email)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    if not data.data:
        st.warning("No AWR reports found")
        st.stop()

    latest = data.data[0]

    metrics = latest["metrics"] or {}
    bottleneck = latest["bottleneck"]
    score = latest["score"]
    level = latest["level"]
    result = latest["result"]

    col1, col2, col3 = st.columns(3)
    col1.metric("CPU %", metrics.get("cpu_pct", 0))
    col2.metric("Health Score", f"{score} ({level})")
    col3.metric("Bottleneck", bottleneck)

    if level == "Critical":
        st.error("🚨 Critical")
    elif level == "Warning":
        st.warning("⚠️ Warning")
    else:
        st.success("✅ Healthy")

    chart = generate_cpu_io_chart(metrics)
    st.image(chart, caption="CPU vs IO")

    st.subheader("🧠 Analysis")
    st.write(result)

# ================= HISTORY =================
if page == "History":

    st.title("📁 AWR History")

    data = supabase.table("awr_reports")\
        .select("*")\
        .eq("user_email", user.email)\
        .order("created_at", desc=True)\
        .execute()

    if not data.data:
        st.warning("No reports yet")
        st.stop()

    for row in data.data:
        st.markdown(f"""
        📄 **{row['created_at']}**  
        ⚡ Score: {row['score']} ({row['level']})  
        🔍 Bottleneck: {row['bottleneck']}
        """)

        if st.button(f"View {row['id']}", key=row["id"]):
            st.write(row["result"])

# ================= FOOTER =================
st.markdown("---")
st.caption("🚀 AI DBA Assistant | JDP | SAAS Application")