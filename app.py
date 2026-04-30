import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
from openai import OpenAI
from bs4 import BeautifulSoup
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from ui_styles import apply_ui_styles, render_centered_title, sidebar_logo

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

# ================= OAUTH HANDLER =================
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

SYSTEM_PROMPT = """
You are a Senior Oracle DBA.
Provide:
- Root Cause
- Fix
- Risks
- Best Practices
"""

# ================= PDF =================
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

# ================= AWR PARSER =================
def parse_awr_html(content):
    soup = BeautifulSoup(content, "lxml")
    return soup.get_text()

# ================= SIDEBAR =================
with st.sidebar:
    sidebar_logo()   # ✅ CORRECT PLACE
    page = st.radio("", ["AI Chat", "Dashboard"])
    st.success(user.email)
    logout()

# ================= MAIN =================
if page == "AI Chat":

    tab1, tab2, tab3 = st.tabs(["Chat", "SQL", "AWR"])

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

    # -------- AWR --------
    with tab3:
        st.subheader("📊 AWR Analyzer")

        file = st.file_uploader("Upload AWR (.txt / .html)", ["txt", "html"])

        if file:
            if st.button("Analyze AWR"):
                content = file.read().decode(errors="ignore")

                if file.name.endswith(".html"):
                    content = parse_awr_html(content)

                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analyze this AWR:\n{content}"}
                    ]
                )

                result = res.choices[0].message.content
                st.write(result)

                pdf = generate_pdf(result, "AWR Report")

                st.download_button(
                    "📄 Download AWR PDF",
                    pdf,
                    file_name="awr_report.pdf",
                    mime="application/pdf"
                )

# ================= FOOTER =================
st.markdown("---")
st.caption("🚀 AI DBA Assistant")