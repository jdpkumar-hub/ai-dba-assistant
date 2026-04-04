import streamlit as st

def admin_page(supabase, username):
    st.header("👑 Admin Dashboard")

    # 🔐 Get role from DB
    result = supabase.table("users").select("role").eq("email", username).execute()

    if not result.data or result.data[0]["role"] != "admin":
        st.error("Access denied ❌")
        return

    # 📊 Get users
    users = supabase.table("users").select("email, role").execute()

    st.subheader("👥 Users")

    for user in users.data:
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.write(user["email"])

        with col2:
            st.write(user["role"])

        with col3:
            if user["role"] == "admin":
                st.write("🔒 Protected")
            else:
                if st.button("Delete", key=user["email"]):
                    supabase.table("users").delete().eq("email", user["email"]).execute()
                    st.success(f"Deleted {user['email']}")
                    st.rerun()