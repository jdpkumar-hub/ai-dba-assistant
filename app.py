import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import io, json

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from ui_styles import apply_ui_styles, render_centered_title, sidebar_logo
from awr_parser import parse_html, extract_metrics, classify_bottleneck, build_awr_prompt, calculate_health_score
from pdf_generator import generate_awr_pdf

# ================= ADMIN =================
ADMIN_EMAILS = ["jdpkumar@gmail.com", "aidbaassistant@gmail.com"]

# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")
apply_ui_styles()
render_centered_title()

# ================= PASSWORD RESET HANDLER =================
query = st.query_params

if query.get("type") == "recovery":

    st.title("🔑 Reset Your Password")

    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Update Password"):

        if new_password != confirm_password:
            st.error("Passwords do not match")
        else:
            try:
                supabase.auth.update_user({"password": new_password})

                st.success("✅ Password updated successfully")
                st.query_params.clear()
                st.info("Please login again")

            except Exception as e:
                st.error("❌ Reset failed")
                st.write(e)

    st.stop()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# 🔥 FIX: force session refresh after OAuth
user = get_user()

if user:
    st.session_state.user = user

# fallback check
if not user:
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state.user = session.user
            user = session.user
    except:
        pass

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

# ================= ADMIN =================
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

# ================= MAIN =================
if page == "AI Chat":

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    with tab1:
        prompt = st.chat_input("Ask...")
        if prompt:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(res.choices[0].message.content)

    with tab2:
        sql = st.text_area("Enter SQL")

        if st.button("Analyze SQL"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sql}]
            )

            result = res.choices[0].message.content
            st.write(result)

    with tab3:
        file = st.file_uploader("Upload AWR", ["txt", "html"])

        if file and st.button("Analyze AWR"):
            content = file.read().decode(errors="ignore")

            if file.name.endswith(".html"):
                content = parse_html(content)

            metrics = extract_metrics(content)
            bottleneck = classify_bottleneck(metrics)

            score, level = calculate_health_score(metrics, bottleneck)

            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": build_awr_prompt(metrics)}]
            )

            result = res.choices[0].message.content
            st.write(result)

            supabase.table("awr_reports").insert({
                "user_email": user.email,
                "metrics": metrics,
                "bottleneck": bottleneck,
                "score": score,
                "level": level,
                "result": result
            }).execute()

            pdf = generate_awr_pdf(result, metrics, score, level)

            st.download_button(
                "📄 Download AWR Report",
                pdf,
                file_name="awr_report.pdf",
                mime="application/pdf"
            )

# ================= ADMIN PANEL =================
if page == "Admin Panel":
    st.title("🛠 Admin Panel")
    data = supabase.table("awr_reports").select("*").execute()
    st.write("Total Reports:", len(data.data))