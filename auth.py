import streamlit as st
from utils import is_strong_password, hash_password, verify_password

# =========================
# 📝 SIGNUP
# =========================
def signup(supabase):
    st.title("📝 Sign Up")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):

        # ✅ Empty check
        if not email or not password:
            st.warning("Please fill all fields")
            return

        # 🔐 Password validation
        if not is_strong_password(password):
            st.warning("Password must contain:\n- 6+ chars\n- 1 uppercase\n- 1 number")
            return

        # 🔍 Check if user exists
        result = supabase.table("users").select("*").eq("email", email).execute()

        if result.data:
            st.warning("⚠️ Email already registered")
            return

        # 🔒 Hash password
        hashed = hash_password(password)

        try:
            supabase.table("users").insert({
                "email": email,
                "password": hashed
            }).execute()

            # ✅ Auto login
            st.session_state.logged_in = True
            st.session_state.username = email

            st.success("Account created & logged in ✅")
            st.rerun()

        except Exception as e:
            st.error("Signup failed ❌")
            st.write(e)


# =========================
# 🔐 LOGIN
# =========================
def login(supabase):
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        result = supabase.table("users").select("*").eq("email", email).execute()

        if result.data:
            stored_password = result.data[0]["password"]

            if verify_password(password, stored_password):
                st.session_state.logged_in = True
                st.session_state.username = email
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Wrong password ❌")
        else:
            st.error("User not found ❌")