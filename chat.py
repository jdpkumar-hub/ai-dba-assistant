import streamlit as st
from openai import OpenAI

# Load OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🤖 AI DBA Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
prompt = st.chat_input("Ask database question...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Oracle DBA assistant.

Help with:
- SQL tuning
- Performance issues
- AWR/ASH analysis
- Indexing strategies
- Wait events
- Execution plans

Give clear, practical, real-world solutions."""
                    }
                ] + st.session_state.messages,
                temperature=0.3
            )

            reply = response.choices[0].message.content
            st.write(reply)

    # Save response
    st.session_state.messages.append({"role": "assistant", "content": reply})