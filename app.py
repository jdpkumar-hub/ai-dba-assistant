import streamlit as st
from openai import OpenAI

# 🔑 Use secrets (for cloud)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🧠 Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# 🎨 Page config
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# 🚀 Title
st.title("🚀 AI Oracle Performance Assistant")

# 🧭 Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Analyze", "💬 History", "ℹ️ About"])

# =========================
# 🔍 TAB 1: ANALYZE
# =========================
with tab1:

    col1, col2 = st.columns(2)

    with col1:
        task = st.selectbox(
            "Select Task",
            ["Query Optimization", "Error Debugging", "Explain SQL", "Performance Issue"]
        )

    with col2:
        st.markdown("### 💡 Tips")
        st.write("Paste SQL or describe your issue clearly")

    # 📝 Input
    user_input = st.text_area("Enter your query or issue:")

    # 📂 File Upload
    uploaded_file = st.file_uploader("Upload SQL file", type=["sql", "txt"])

    file_content = ""
    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")
        st.subheader("📄 File Content")
        st.code(file_content, language="sql")

    # ▶️ DB Button
    if st.button("Run SQL on DB"):
        st.info("⚠️ Database feature works only in local environment")

    # 🤖 Analyze Button
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

                    st.session_state.history.append(("User", input_data))
                    st.session_state.history.append(("AI", ai_reply))

            except Exception as e:
                st.error("⚠️ API Error")
                st.write(str(e))
        else:
            st.warning("Please enter input or upload file")

    # 🧹 Clear history
    if st.button("Clear History"):
        st.session_state.history = []

# =========================
# 💬 TAB 2: HISTORY
# =========================
with tab2:
    st.subheader("💬 Conversation History")

    for role, msg in st.session_state.history:
        if role == "User":
            st.markdown(f"**🧑‍💻 You:** {msg}")
        else:
            st.markdown(f"**🤖 AI:** {msg}")

# =========================
# ℹ️ TAB 3: ABOUT
# =========================
with tab3:
    st.subheader("ℹ️ About This App")

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