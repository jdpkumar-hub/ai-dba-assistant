import streamlit as st
from openai import OpenAI
import bcrypt
from supabase import create_client

# =========================
# 🔑 KEYS
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# =========================
# 🎨 PAGE CONFIG
# =========================
st.set_page_config(page_title="AI DBA Assistant", layout="wide")

# =========================
# 🧠 SESSION STATE
# =========================
if "history" not in st.session_state:
    st.session_state.history = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# =========================
# 🔐 SIGNUP (SUPABASE)
# =========================
def signup():
    st.title("📝 Sign Up")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Create Account"):
        if new_user and new_pass:
            hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()

            try:
                supabase.table("users").insert({
                    "username": new_user,
                    "password": hashed
                }).execute()

                st.success("Account created ✅")

            except Exception as e:
                st.error("User already exists or error ❌")
                st.write(e)
        else:
            st.warning("Fill all fields")

# =========================
# 🔐 LOGIN (SUPABASE)
# =========================
def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = supabase.table("users").select("*").eq("username", username).execute()

        if result.data:
            stored_password = result.data[0]["password"].encode()

            if bcrypt.checkpw(password.encode(), stored_password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Wrong password ❌")
        else:
            st.error("User not found ❌")

# =========================
# 🚪 LOGOUT
# =========================
def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# =========================
# 🔐 AUTH SCREEN
# =========================
if not st.session_state.logged_in:

    menu_auth = st.sidebar.selectbox("Account", ["Login", "Sign Up"])

    if menu_auth == "Login":
        login()
    else:
        signup()

# =========================
# 🚀 MAIN APP
# =========================
else:

    st.sidebar.title("🚀 AI DBA Assistant")
    st.sidebar.write(f"👤 {st.session_state.username}")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "📌 Navigation",
        ["Analyze", "History", "About"]
    )

    logout()

    st.title("🚀 AI Oracle Performance Assistant")

    # =========================
    # 🔍 ANALYZE
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

        user_input = st.text_area("Enter your query or issue:")
        uploaded_file = st.file_uploader("Upload SQL file", type=["sql", "txt"])

        file_content = ""
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode("utf-8")

            with st.expander("📄 View Uploaded SQL"):
                st.code(file_content, language="sql")

        if st.button("Analyze"):

            input_data = file_content if file_content else user_input

            if input_data:
                prompt = f"""
                You are an expert Oracle DBA.

                Task: {task}

                Analyze and provide solution for:
                {input_data}
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

                        st.session_state.history.append(("User", input_data))
                        st.session_state.history.append(("AI", ai_reply))

                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Enter input or upload file")

    # =========================
    # 💬 HISTORY
    # =========================
    elif menu == "History":

        st.header("💬 Conversation History")

        for role, msg in st.session_state.history:
            if role == "User":
                st.markdown(f"**🧑‍💻 You:** {msg}")
            else:
                st.markdown(f"**🤖 AI:** {msg}")

    # =========================
    # ℹ️ ABOUT
    # =========================
    elif menu == "About":

        st.header("ℹ️ About")

        st.write("""
        AI-powered Oracle Performance Assistant  
        Built using Streamlit + OpenAI + Supabase 🚀
        """)

    st.markdown("---")
    st.caption("Built by Prem Kumar 🚀")