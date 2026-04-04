import streamlit as st

def analyze_page(client):

    st.header("🔍 Analyze SQL")

    # =========================
    # 🎯 TASK SELECTION
    # =========================
    task = st.selectbox(
        "Select Task",
        ["Query Optimization", "Error Debugging", "Explain SQL", "Performance Issue"]
    )

    # =========================
    # 📥 INPUT
    # =========================
    user_input = st.text_area("Enter your query or issue:")

    uploaded_file = st.file_uploader("Upload SQL file", type=["sql", "txt"])

    file_content = ""

    if uploaded_file is not None:
        file_content = uploaded_file.read().decode("utf-8")

        with st.expander("📄 View Uploaded SQL"):
            st.code(file_content, language="sql")

    # =========================
    # 🚀 ANALYZE BUTTON
    # =========================
    if st.button("Analyze"):

        input_data = file_content if file_content else user_input

        if input_data:

            # 🧠 Prompt
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

                Analyze and provide solution:
                {input_data}
                """

            try:
                with st.spinner("Analyzing..."):
                    response = client.chat.completions.create(
                        model="gpt-4.1-mini",
                        messages=[{"role": "user", "content": prompt}]
                    )

                    ai_reply = response.choices[0].message.content

                    # =========================
                    # 📊 OUTPUT
                    # =========================
                    st.subheader("📊 Results")
                    st.write(ai_reply)

                    # Save history
                    st.session_state.history.append(("User", input_data))
                    st.session_state.history.append(("AI", ai_reply))

            except Exception as e:
                st.error("Error occurred")
                st.write(e)

        else:
            st.warning("Please enter input or upload file")