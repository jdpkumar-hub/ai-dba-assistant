import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
import os
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="AI DBA Assistant", page_icon="🤖", layout="wide")

# -------------------------------
# OPENAI
# -------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# SESSION INIT
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------------
# PDF GENERATOR
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# OAUTH HANDLER
# -------------------------------
params = st.query_params

if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })
        st.query_params.clear()

        user = get_user()
        if user:
            st.session_state.user = user

        st.rerun()

    except Exception as e:
        st.error(f"Login failed: {e}")

# -------------------------------
# AUTH CHECK
# -------------------------------
user = get_user()
if user:
    st.session_state.user = user

user = st.session_state.user

if not user:
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "🆕 Signup", "🔑 Reset"])

    with tab1:
        login()
    with tab2:
        signup()
    with tab3:
        reset_password()

    st.stop()

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    st.title("AI DBA Assistant")

    page = st.radio("", [
        "🏠 Dashboard",
        "💬 AI Chat",
        "📊 Performance Diagnostics",
        "📜 History",
        "⚙️ Settings"
    ])

    st.success(user.email)
    logout()

# ===============================
# DASHBOARD
# ===============================
if page == "🏠 Dashboard":
    st.title("🚀 AI DBA Assistant")
    st.markdown("### Smart Oracle Optimization Platform")

    col1, col2, col3 = st.columns(3)

    col1.metric("Active Users", "12")
    col2.metric("Queries Analyzed", "320")
    col3.metric("Reports Generated", "58")

# ===============================
# AI CHAT
# ===============================
elif page == "💬 AI Chat":
    st.title("💬 AI DBA Assistant")

    question = st.text_input("Ask any Oracle DBA question:")

    if question:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}]
            )

            answer = response.choices[0].message.content

            st.success("Response:")
            st.write(answer)

            pdf = create_pdf(answer)
            st.download_button("📄 Download as PDF", pdf, "ai_response.pdf")

# ===============================
# PERFORMANCE DIAGNOSTICS
# ===============================
elif page == "📊 Performance Diagnostics":
    st.title("📊 AWR Performance Analyzer")

    file = st.file_uploader("Upload AWR Report (.txt)", type=["txt"])

    if file:
        content = file.read().decode("utf-8")

        st.success("File uploaded successfully!")

        if st.button("🔍 Analyze Report"):
            with st.spinner("Analyzing AWR..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user",
                        "content": f"Analyze this Oracle AWR report and give key findings:\n{content[:15000]}"
                    }]
                )

                result = response.choices[0].message.content

                st.subheader("📈 Analysis Result")
                st.write(result)

# ===============================
# HISTORY
# ===============================
elif page == "📜 History":
    st.title("📜 History")
    st.info("History feature coming soon...")

# ===============================
# SETTINGS
# ===============================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.info("Settings coming soon...")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("© AI DBA Assistant 🚀")