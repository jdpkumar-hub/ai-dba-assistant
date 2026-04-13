import streamlit as st
from auth import login, signup, reset_password, logout, get_user, supabase
import os
from openai import OpenAI
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# -------------------------------
# 🔐 SESSION INIT
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------------
# 👑 ADMIN CONFIG
# -------------------------------
ADMIN_EMAIL = "aidbaassistant@gmail.com"   # 👈 change to your email

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def is_admin(user):
    return user and user.email == ADMIN_EMAIL
    
# -------------------------------
# PDF GENERATOR
# -------------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 10))
            continue

        if line.startswith("###") or line.startswith("##"):
            story.append(Paragraph(f"<b>{line.replace('#','').strip()}</b>", styles["Heading2"]))
        else:
            story.append(Paragraph(line, styles["Normal"]))

        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# 🔐 HANDLE OAUTH CALLBACK
# -------------------------------
params = st.query_params

# Password reset handler
if "type" in params and params["type"] == "recovery":
    st.session_state.reset_mode = True
    st.query_params.clear()
    st.rerun()

# OAuth handler (FIXED)
if "code" in params:
    try:
        supabase.auth.exchange_code_for_session({
            "auth_code": params["code"]
        })

        st.query_params.clear()

        user = get_user()
        if user and not st.session_state.user:
            st.session_state.user = user
            st.rerun()

    except Exception as e:
        st.error(f"Login failed: {e}")

# -------------------------------
# OPENAI CLIENT
# -------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI DBA Assistant", page_icon="🤖", layout="wide")

# -------------------------------
# STYLE
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
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# USER SESSION
# -------------------------------
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
    pages = ["🏠 Dashboard", "💬 AI Chat", "📊 Reports", "📜 History", "⚙️ Settings"]
        if is_admin(user):
            pages.append("👑 Admin Panel")
     page = st.radio("", pages)   
    st.success(user.email)
    logout()

# ================= DASHBOARD =================
if page == "🏠 Dashboard":
    st.title("📊 Dashboard")

    try:
        data = supabase.table("query_history")\
            .select("*")\
            .eq("user_email", user.email)\
            .execute()

        df = pd.DataFrame(data.data)

        if not df.empty:
            col1, col2 = st.columns(2)
            col1.metric("Total Queries", len(df))

            df["created_at"] = pd.to_datetime(df["created_at"])
            df["date"] = df["created_at"].dt.date
            col2.metric("Active Days", df["date"].nunique())

            st.subheader("📈 Queries Trend")
            st.line_chart(df.groupby("date").size())

            def classify(q):
                if "AWR" in q:
                    return "AWR"
                elif "select" in q.lower():
                    return "SQL"
                else:
                    return "Chat"

            df["type"] = df["question"].apply(classify)
            st.subheader("📊 Usage Breakdown")
            st.bar_chart(df["type"].value_counts())

        else:
            st.info("No data yet")

    except Exception:
        st.error("Error loading dashboard")

# ================= AI CHAT =================
elif page == "💬 AI Chat":
    st.title("AI DBA Assistant")

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "⚡ SQL Analyzer", "📊 AWR Analyzer"])

    with tab1:
        question = st.text_input("Ask anything...")

        if question:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}]
            )
            answer = response.choices[0].message.content
            st.write(answer)

            pdf_file = create_pdf(answer)
            st.download_button("📄 Download Report", pdf_file, "report.pdf")

    with tab2:
        sql = st.text_area("Paste SQL")

        if st.button("Analyze"):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sql}]
            )
            answer = response.choices[0].message.content
            st.write(answer)

            pdf_file = create_pdf(answer)
            st.download_button("📄 Download Report", pdf_file, "report.pdf")

    with tab3:
        file = st.file_uploader("Upload AWR", type=["txt"])

        if file:
            content = file.read().decode("utf-8")[:15000]

            if st.button("Analyze AWR"):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": content}]
                )
                st.write(response.choices[0].message.content)

# ================= HISTORY =================
elif page == "📜 History":
    st.title("📜 Query History")

# ================= REPORTS =================
elif page == "📊 Reports":
    st.title("Reports")

# ================= SETTINGS =================
elif page == "⚙️ Settings":
    st.title("Settings")
    

# ================= ADMIN PANEL =================
elif page == "👑 Admin Panel":

    st.title("👑 Admin Panel")

    if not is_admin(user):
        st.error("Access Denied")
        st.stop()

    # ---------------- USERS ----------------
    st.subheader("👥 All Users")

    try:
        users = admin_client.auth.admin.list_users()

        user_data = []

        for u in users:
            user_data.append({
                "Email": u.email,
                "Created": u.created_at,
                "Last Login": u.last_sign_in_at
            })

        df = pd.DataFrame(user_data)
        st.dataframe(df)

    except Exception as e:
        st.error(f"Error fetching users: {e}")

    # ---------------- METRICS ----------------
    st.subheader("📊 Activity Overview")

    total_users = len(user_data)
    active_users = sum(1 for u in user_data if u["Last Login"])

    col1, col2 = st.columns(2)
    col1.metric("Total Users", total_users)
    col2.metric("Active Users", active_users)

    # ---------------- DELETE USER ----------------
    st.subheader("🗑️ Delete User")

    email_to_delete = st.text_input("Enter email to delete")

    if st.button("Delete User"):
        try:
            for u in users:
                if u.email == email_to_delete:
                    admin_client.auth.admin.delete_user(u.id)
                    st.success("User deleted")
                    st.rerun()

            st.warning("User not found")

        except Exception as e:
            st.error(f"Delete failed: {e}")
    
# =========================
# 📌 FOOTER
# =========================
st.markdown("---")
st.caption("© AI DBA Assistant | Built by Pradarshan Kumar JD 🚀")