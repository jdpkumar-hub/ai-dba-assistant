import streamlit as st
from auth import login, logout

# -------------------------------
# ⚙️ PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="AI DBA Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# 🔐 AUTH CHECK
# -------------------------------
if not login():
    st.stop()   # ⛔ Stop app until logged in


# -------------------------------
# 🎉 MAIN APP UI
# -------------------------------
st.title("🤖 AI DBA Assistant")

st.success("✅ You are logged in!")

# Sidebar
with st.sidebar:
    st.markdown("### 👤 User Panel")
    st.write("Logged in successfully")

    if st.button("🚪 Logout"):
        logout()


# -------------------------------
# 💬 CHAT UI (BASIC)
# -------------------------------
st.markdown("### 💬 Ask your database question")

user_input = st.text_input("Type your question...")

if user_input:
    st.write("🤖 AI Response:")
    st.info(f"You asked: {user_input}")

    # (Later we connect OpenAI here)