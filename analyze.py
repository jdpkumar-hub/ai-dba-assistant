import streamlit as st

def analyze_page(client):
    st.header("🔍 Analyze SQL")

    user_input = st.text_area("Enter query")

    if st.button("Analyze"):

        if user_input:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": user_input}]
            )

            st.write(response.choices[0].message.content)