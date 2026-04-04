import streamlit as st

def admin_page(supabase, username):
    st.header("👑 Admin Dashboard")

    # 🔒 Only admin can access
    if username != "admin":
        st.error("Access denied ❌")
        return

    # 📊 Fetch users
    result = supabase.table("users").select("email").execute()

    st.subheader("👥 Registered Users")

    # 🔁 Loop through users
    for user in result.data:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(user["email"])

        with col2:
            # 🚫 Protect admin user
            if user["email"] == "admin":
                st.write("🔒 Protected")
            else:
                if st.button("Delete", key=user["email"]):
                    supabase.table("users").delete().eq("email", user["email"]).execute()
                    st.success(f"Deleted {user['email']}")
                    st.rerun()
                