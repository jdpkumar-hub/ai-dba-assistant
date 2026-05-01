import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import io
import json

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from ui_styles import apply_ui_styles, render_centered_title, sidebar_logo
from awr_parser import parse_html, extract_metrics, classify_bottleneck, build_awr_prompt, calculate_health_score
from pdf_generator import generate_awr_pdf, generate_cpu_io_chart

# ================= ADMIN =================
ADMIN_EMAILS = ["jdpkumar@gmail.com", "aidbaassistant@gmail.com"]

# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")
apply_ui_styles()
render_centered_title()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

# ✅ SAFE SESSION FIX (no full clear)
if "last_user" not in st.session_state:
    st.session_state.last_user = None

if user and st.session_state.last_user != user.email:
    st.session_state.last_user = user.email

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

# ================= ADMIN CHECK =================
is_admin = user.email in ADMIN_EMAILS

# ================= SIDEBAR =================
with st.sidebar:
    sidebar_logo()

    pages = ["AI Chat", "Dashboard", "History", "Trends"]

    if is_admin:
        pages.append("Admin Panel")

    page = st.radio("", pages)

    st.success(user.email)
    logout()

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

            # ✅ SAVE TO DB
            try:
                supabase.table("awr_reports").insert({
                    "user_email": str(user.email),
                    "metrics": json.loads(json.dumps(metrics)),
                    "bottleneck": str(bottleneck),
                    "score": int(score),
                    "level": str(level),
                    "result": str(result)
                }).execute()

                st.success("✅ AWR report saved")

            except Exception as e:
                st.error("❌ Failed to save AWR report")
                st.write(e)

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

    st.write(result)

# ================= ADMIN =================
if page == "Admin Panel":
    st.title("🛠 Admin Panel")

    data = supabase.table("awr_reports").select("*").execute()

    st.write("Total Reports:", len(data.data))

    for row in data.data[:10]:
        st.write(row["user_email"], row["score"], row["created_at"])

# ================= FOOTER =================
st.markdown("---")
st.caption("🚀 AI DBA Assistant")