import streamlit as st
from openai import OpenAI

# 🎨 Page config
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# 🔑 API Key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🧠 Session state
if "history" not in st.session_state:
    st.session_state.history = []

# 🎨 Sidebar (SaaS Navigation)
st.sidebar.title("🚀 AI DBA Assistant")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "📌 Navigation",
    ["Analyze", "History", "About"]
)

# 🚀 Title
st.title("🚀 AI Oracle Performance Assistant")

# =========================
# 🔍 ANALYZE PAGE
# =========================
if menu == "Analyze":

    st.header("🔍 Analyze SQL")

    col1, col2 = st.columns(2)

    with col1:
        task = st.selectbox(
            "Select Task",
            ["Query Optimization", "Error Debugging", "Explain SQL", "Performance Issue"]
        )

    with col2:
        st.markdown("### 💡 Tips")
        st.write("Paste SQL or describe your issue clearly")

    st.subheader("📥 Input")

    user_input = st.text_area("Enter your query or issue:")

    uploaded_file = st.file_uploader("Upload SQL file", type=["sql", "txt"])

    file_content = ""

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")

        with st.expander("📄 View Uploaded SQL"):
            st.code(file_content, language="sql")

    # ▶️ DB Button
    if st.button("Run SQL on DB"):
        st.info("⚠️ Database feature works only in local environment")

    # 🤖 Analyze
    if st.button("Analyze"):

        input_data = file_content if file_content else user_input

        if input_data:
            if task == "Query Optimization":
                prompt = f"""
                You are an expert Oracle DBA.

                Optimize this SQL query for performance.
                Provide:
                1. Optimized query
                2. Explanation
                3. Index suggestions

                SQL:
                {input_data}
                """
            else:
                prompt = f"""
                You are an expert Oracle DBA.

                Task: {task}
                User Input: {input_data}

                Provide clear and practical solution.
                """

            try:
                with st.spinner("Analyzing..."):
                    response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    ai_reply = response.choices[0].message.content

                    st.subheader("📊 Results")
                    st.write(ai_reply)

                    # Save history
                    st.session_state.history.append(("User", input_data))
                    st.session_state.history.append(("AI", ai_reply))

            except Exception as e:
                st.error("⚠️ API Error")
                st.write(str(e))
        else:
            st.warning("Please enter input or upload file")

    # Clear history
    if st.button("Clear History"):
        st.session_state.history = []

# =========================
# 💬 HISTORY PAGE
# =========================
elif menu == "History":

    st.header("💬 Conversation History")

    for role, msg in st.session_state.history:
        if role == "User":
            st.markdown(f"**🧑‍💻 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")

# =========================
# ℹ️ ABOUT PAGE
# =========================
elif menu == "About":

    st.header("ℹ️ About")

    st.write("""
    This is an AI-powered Oracle Performance Assistant.

    Features:
    - SQL Optimization
    - Query Analysis
    - File Upload Support
    - AI Recommendations

    Built using:
    - Streamlit
    - OpenAI API
    """)

# 🎯 Footer
st.markdown("---")
st.caption("Built by Pradarshan Kumar JD | AI DBA Assistant")