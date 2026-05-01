import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
from bs4 import BeautifulSoup
import io
import pandas as pd
import json

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from awr_pdf import generate_awr_pdf
from ui_styles import apply_ui_styles, render_centered_title, sidebar_logo
from admin_panel import render_admin
from usage_tracker import track_usage

from awr_parser import (
    parse_html,
    extract_metrics,
    classify_bottleneck,
    build_awr_prompt,
    calculate_health_score
)
from otp_auth import signup_with_otp, reset_with_otp
from awr_parser import extract_metrics, classify_bottleneck, build_awr_prompt, calculate_health_score

# ================= ADMIN =================
ADMIN_EMAILS = ["jdpkumar@gmail.com", "aidbaassistant@gmail.com"]


# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")
apply_ui_styles()
render_centered_title()

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= OAUTH HANDLER =================
params = st.query_params
if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })
        st.session_state.user = supabase.auth.get_session().user
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"OAuth Error: {e}")

user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user
#========================================
# ================= PASSWORD RECOVERY =================
query_params = st.query_params

if query_params.get("type") == "recovery":
    st.title("🔑 Reset Your Password")

    new_password = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        try:
            supabase.auth.update_user({
                "password": new_password
            })

            st.success("✅ Password updated successfully!")
            st.info("Please login with your new password.")
        except Exception as e:
            st.error("❌ Failed to update password")
            st.write(e)

    st.stop()
# ================= LOGIN =================
if not user:
    col1, col2 = st.columns([0.8, 2.0])

    with col1:
        st.image("image/logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization")

    with col2:
#        tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])
#        with tab1: login()
#        with tab2: signup()
#        with tab3: reset_password()
        
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])
        with tab1:
            login()   # ✅ KEEP GOOGLE AUTH UNCHANGED
        with tab2:
            signup_with_otp()   # ✅ NEW OTP SIGNUP
        with tab3:
            reset_with_otp()    # ✅ NEW RESET FLOW

    st.stop()

# ================= OPENAI =================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ================= PDF =================
def generate_pdf(text, title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = [Paragraph(title, styles["Title"]), Spacer(1, 10)]

    for line in text.split("\n"):
        if line.strip():
            content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ================= AWR PARSER =================
def parse_awr_html(content):
    soup = BeautifulSoup(content, "lxml")
    return soup.get_text()

# ================= SIDEBAR =================
with st.sidebar:
    sidebar_logo()

    pages = ["AI Chat", "Dashboard", "History", "Trends"]

    # ✅ SHOW ADMIN ONLY IF ADMIN
    if user.email in ADMIN_EMAILS:
        pages.append("Admin")

    page = st.radio("", pages)

    st.success(user.email)
    logout()
# ================= AI CHAT =================
if page == "AI Chat":

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    # CHAT
    with tab1:
        prompt = st.chat_input("Ask...")
        if prompt:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(res.choices[0].message.content)

    # SQL
    with tab2:
        sql = st.text_area("Enter SQL")

        if st.button("Analyze SQL"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sql}]
            )

            result = res.choices[0].message.content
            st.write(result)
            track_usage(user.email, "SQL_ANALYSIS")
            pdf = generate_pdf(result, "SQL Report")
            st.download_button(
                "📄 Download AWR PDF",
                data=pdf.getvalue(),
                file_name="awr_report.pdf",
                mime="application/pdf"
            )

  # ================= AWR =================
    # ================= AWR =================
    with tab3:
        st.subheader("📊 Upload AWR Report")

        file = st.file_uploader("Upload AWR (.html or .txt)", type=["html", "txt"])

        if file is not None:
            st.success(f"Uploaded: {file.name}")

        if file is not None and st.button("Analyze AWR"):
            content = file.read().decode(errors="ignore")

            if file.name.endswith(".html"):
                content = parse_awr_html(content)

            # ✅ STEP 1: Extract
            metrics = extract_metrics(content)

            # ✅ STEP 2: Classify
            bottleneck = classify_bottleneck(metrics)

            st.json(metrics)
            st.info(f"Detected Bottleneck: {bottleneck}")

            # ✅ STEP 5: Score
            score = calculate_health_score(metrics)
            st.metric("Health Score", score)

            # ✅ STEP 3: Smart prompt
            prompt = build_awr_prompt(metrics, bottleneck)

            # ✅ AI call
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert Oracle DBA."},
                    {"role": "user", "content": prompt}
                ]
            )

            result = res.choices[0].message.content
            st.write(result)

            # ✅ Save in session (fix crash)
            st.session_state.awr_result = result
            st.session_state.awr_pdf = generate_pdf(result, "AWR Report")

            # ✅ Download
            st.download_button(
                "📄 Download AWR PDF",
                data=st.session_state.awr_pdf.getvalue(),
                file_name="awr_report.pdf",
                mime="application/pdf"
            )

            # ================= DISPLAY =================
            if st.session_state.awr_result:

                st.write(st.session_state.awr_result)

                st.download_button(
                    "📄 Download AWR PDF",
                    data=st.session_state.awr_pdf.getvalue(),
                    file_name="awr_report.pdf",
                    mime="application/pdf"
                )
# ================= DASHBOARD =================
if page == "Dashboard":
    st.title("📊 Dashboard")

    data = supabase.table("awr_reports")\
        .select("*")\
        .eq("user_email", user.email)\
        .execute()

    if data.data:
        st.metric("Total Reports", len(data.data))
    else:
        st.info("No data yet")

# ================= HISTORY =================
if page == "History":
    st.title("🕘 AWR History")

    data = supabase.table("awr_reports")\
        .select("*")\
        .eq("user_email", user.email)\
        .order("created_at", desc=True)\
        .execute()

    if data.data:
        for row in data.data:
            with st.expander(row["created_at"]):
                st.write(row["result"])
    else:
        st.info("No reports found")

# ================= TRENDS =================
if page == "Trends":
    st.title("📈 Trends")

    data = supabase.table("awr_reports")\
        .select("*")\
        .eq("user_email", user.email)\
        .execute()

    if not data.data:
        st.warning("No data")
        st.stop()

    df = pd.DataFrame(data.data)
    df["created_at"] = pd.to_datetime(df["created_at"])

    df["count"] = range(len(df))

    st.line_chart(df.set_index("created_at")["count"])
    
#==================================
if page == "Admin":
        if user.email in ADMIN_EMAILS:
            render_admin(user)
        else:
            st.error("Unauthorized access")