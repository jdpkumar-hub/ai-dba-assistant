import streamlit as st

def login():
    st.title("🔐 Login")

    st.markdown("### Continue with Google")
    st.markdown(
        """
        <a href="https://ai-auth-frontend-nine.vercel.app">
            <button style="
                padding:12px;
                border-radius:8px;
                border:none;
                background-color:#4285F4;
                color:white;
                font-size:16px;
                cursor:pointer;">
                🔵 Continue with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.info("Login using Google to access AI DBA Assistant")