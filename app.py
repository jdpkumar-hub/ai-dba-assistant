import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import pandas as pd
from bs4 import BeautifulSoup

# NEW IMPORTS
import io, datetime, zipfile, smtplib
import matplotlib.pyplot as plt
from email.message import EmailMessage
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

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

# ================= OPENAI =================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
You are a Senior Oracle DBA.
Provide:
- Root Cause
- Diagnostic Queries
- Fix Steps
- Risks
- Best Practices
"""

# ================= PDF + CHART =================
def generate_chart(text):
    cpu, io_wait = 60, 40
    fig = plt.figure()
    plt.bar(["CPU", "IO"], [cpu, io_wait])

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
    content.append(Paragraph("<b>AI DBA Assistant</b>", styles["Title"]))
    content.append(Paragraph(title, styles["Heading2"]))
    content.append(Spacer(1, 10))

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    content.append(PageBreak())

    chart = generate_chart(text)
    content.append(Paragraph("CPU vs IO", styles["Heading2"]))
    content.append(Image(chart, width=400, height=200))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ================= EMAIL =================
def send_email(user_email, pdf):
    try:
        msg = EmailMessage()
        msg["Subject"] = "AI DBA Report"
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = user_email

        msg.set_content("Your report attached.")

        msg.add_attachment(
            pdf.getvalue(),
            maintype="application",
            subtype="pdf",
            filename="report.pdf"
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
            smtp.send_message(msg)

    except Exception as e:
        st.error(f"Email error: {e}")

# ================= STORAGE =================
def upload_pdf(user, file_name, pdf):
    try:
        supabase.storage.from_("reports").upload(
            f"{user.email}/{file_name}",
            pdf.getvalue(),
            {"content-type": "application/pdf"}
        )
    except Exception as e:
        st.error(f"Upload error: {e}")

def download_all(user):
    try:
        files = supabase.storage.from_("reports").list(user.email)
        zip_buf = io.BytesIO()

        with zipfile.ZipFile(zip_buf, "w") as z:
            for f in files:
                data = supabase.storage.from_("reports").download(
                    f"{user.email}/{f['name']}"
                )
                z.writestr(f["name"], data)

        zip_buf.seek(0)

        st.download_button("📁 Download All Reports", zip_buf, "reports.zip")

    except Exception as e:
        st.error(e)

# ================= PLAN =================
def is_pro(user):
    try:
        data = supabase.table("user_plans").select("*").eq("email", user.email).execute()
        return data.data and data.data[0]["plan"] == "pro"
    except:
        return False

# ================= AWR PARSER =================
def parse_html(content):
    soup = BeautifulSoup(content, "lxml")
    return soup.get_text()

# ================= USER =================
user = get_user()
if not user:
    tab1, tab2, tab3 = st.tabs(["Login", "Signup", "Reset"])
    with tab1: login()
    with tab2: signup()
    with tab3: reset_password()
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    page = st.radio("", ["AI Chat", "Dashboard", "History"])
    st.success(user.email)
    logout()

# ================= DASHBOARD =================
if page == "Dashboard":
    st.title("Dashboard")

# ================= AI CHAT =================
elif page == "AI Chat":
    st.title("AI DBA Assistant")

    tab1, tab2, tab3 = st.tabs(["Chat", "SQL", "AWR"])

    # -------- CHAT --------
    with tab1:
        prompt = st.chat_input("Ask...")
        if prompt:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"system","content":SYSTEM_PROMPT},
                          {"role":"user","content":prompt}]
            )
            st.write(res.choices[0].message.content)

    # -------- SQL --------
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

                if st.button("📧 Email"):
                    send_email(user.email, pdf)
            else:
                st.warning("🔒 Pro only")

    # -------- AWR --------
    with tab3:
        file = st.file_uploader("Upload AWR", ["txt", "html"])
        if file:
            content = file.read().decode(errors="ignore")

            if file.name.endswith(".html"):
                content = parse_html(content)

            if st.button("Analyze AWR"):
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

                    if st.button("📧 Email"):
                        send_email(user.email, pdf)
                else:
                    st.warning("🔒 Pro only")

# ================= HISTORY =================
elif page == "History":
    st.title("History")
    download_all(user)

# ================= FOOTER =================
st.markdown("---")
st.caption("AI DBA Assistant SaaS 🚀")