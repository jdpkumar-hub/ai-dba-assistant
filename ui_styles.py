import streamlit as st

def apply_ui_styles():
    st.markdown("""
    <style>

    /* Page padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Center main content */
    .main > div {
        max-width: 1200px;
        margin: auto;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        padding: 20px;
    }

    /* Chat input width */
    .stChatInputContainer {
        max-width: 900px;
        margin: auto;
    }

    /* Buttons */
    .stButton button {
        border-radius: 10px;
        padding: 10px 16px;
        margin: 4px;
    }

    /* Title styling */
    h1 {
        text-align: center;
    }

    </style>
    """, unsafe_allow_html=True)


def render_centered_title():
    st.markdown(
        "<h1>🤖 AI DBA Assistant</h1>",
        unsafe_allow_html=True
    )


def sidebar_logo():
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image("image/logo2.png", width=160)
    st.markdown("</div>", unsafe_allow_html=True)