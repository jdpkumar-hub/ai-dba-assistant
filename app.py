import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
import pandas as pd
from bs4 import BeautifulSoup

import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ================= CONFIG =================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# ================= CSS =================
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()
# ===============================
# 🔐 GOOGLE OAUTH HANDLER
# ===============================
params = st.query_params

if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })

        st.query_params.clear()

        st.session_state.user = supabase.auth.get_session().user

        st.rerun()

    except Exception as e:
        st.error(f"OAuth Error: {e}")

# ================= OAUTH FIX =================
params = st.query_params
if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })
        st.query_params.clear()
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

# ================= PDF =================
def generate_pdf(text, title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(title, styles["Title"]))
    content.append(Spacer(1, 10))

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    return buffer

# ================= SIDEBAR =================
with st.sidebar:
    page = st.radio("", ["AI Chat", "Dashboard"])
    st.success(user.email)
    logout()

# ================= MAIN =================
if page == "AI Chat":

    tab1, tab2 = st.tabs(["Chat", "SQL"])

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
                "📄 Download PDF",
                pdf,
                file_name="sql_report.pdf",
                mime="application/pdf"
            )