import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import pandas as pd
from bs4 import BeautifulSoup

import io, datetime, zipfile, smtplib
import matplotlib.pyplot as plt
from email.message import EmailMessage

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", page_icon="🤖", layout="wide")

# ================= CSS =================
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass
load_css()

# ================= SESSION FIX =================
if "user" not in st.session_state:
    st.session_state.user = None

user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

# ================= LOGIN UI =================
if not user:
    col1, col2 = st.columns([1.4, 0.8])

    with col1:
        st.image("image/logo2.png", width=220)
        st.markdown("## AI DBA Assistant")
        st.caption("🚀 Smart Oracle Optimization")

    with col2:
        tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Reset"])
        with tab1: login()
        with tab2: signup()
        with tab3: reset_password()

    st.stop()

# ================= OPENAI =================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """You are a Senior Oracle DBA"""

# ================= PDF =================
def generate_chart():
    fig = plt.figure()
    plt.bar(["CPU", "IO"], [60, 40])
    buf = io.BytesIO()
    plt.savefig(buf)
    plt.close()
    buf.seek(0)
    return buf

def generate_pdf(text, title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(title, styles["Title"]))

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    content.append(PageBreak())
    content.append(Image(generate_chart(), width=400, height=200))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ================= STORAGE =================
def upload_pdf(user, name, pdf):
    try:
        supabase.storage.from_("reports").upload(
            f"{user.email}/{name}",
            pdf.getvalue(),
            {"content-type": "application/pdf"}
        )
    except Exception as e:
        st.error(e)

# ================= EMAIL =================
def send_email(user_email, pdf):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Report"
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = user_email
        msg.set_content("Attached")

        msg.add_attachment(pdf.getvalue(),
            maintype="application", subtype="pdf", filename="report.pdf")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
            s.send_message(msg)
    except Exception as e:
        st.error(e)

# ================= PRO CHECK =================
def is_pro(user):
    try:
        data = supabase.table("user_plans").select("*").eq("email", user.email).execute()
        return data.data and data.data[0]["plan"] == "pro"
    except:
        return False

# ================= SIDEBAR =================
with st.sidebar:
    page = st.radio("", ["AI Chat", "Dashboard", "History"])
    st.success(user.email)
    logout()

# ================= AI CHAT =================
if page == "AI Chat":

    tab1, tab2, tab3 = st.tabs(["Chat", "SQL", "AWR"])

    with tab1:
        q = st.chat_input("Ask...")
        if q:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":q}]
            )
            st.write(res.choices[0].message.content)

    with tab2:
        sql = st.text_area("SQL")
        if st.button("Analyze SQL"):
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":sql}]
            )
            result = res.choices[0].message.content
            st.write(result)

            if is_pro(user):
                pdf = generate_pdf(result, "SQL Report")
                st.download_button("📄 PDF", pdf, "sql.pdf")
                upload_pdf(user, "sql.pdf", pdf)

    with tab3:
        file = st.file_uploader("Upload AWR", ["txt","html"])
        if file and st.button("Analyze AWR"):
            content = file.read().decode(errors="ignore")

            if file.name.endswith(".html"):
                content = BeautifulSoup(content, "lxml").get_text()

            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":content}]
            )
            result = res.choices[0].message.content
            st.write(result)

            if is_pro(user):
                pdf = generate_pdf(result, "AWR Report")
                st.download_button("📄 PDF", pdf, "awr.pdf")
                upload_pdf(user, "awr.pdf", pdf)

# ================= HISTORY =================
if page == "History":
    st.title("Reports")
    st.info("Coming soon")
