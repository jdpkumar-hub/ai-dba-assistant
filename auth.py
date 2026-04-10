import streamlit as st

def login():
    st.title("🔐 Login")

    st.markdown("### Continue with Google")
    st.markdown(
        """
        <a href="https://ai-auth-frontend-nine.vercel.app">
            <button style="
                padding:10px;
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
    st.markdown("### Or login with Email")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        st.success("Login logic here")