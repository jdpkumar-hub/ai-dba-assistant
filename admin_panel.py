import streamlit as st
from auth import supabase

ADMIN_EMAILS = ["jdpkumar@gmail.com","aidbaassistant@gmail.com"]


def render_admin(user):
    if user.email not in ADMIN_EMAILS:
        return

    st.title("🛠 Admin Panel")

    data = supabase.table("awr_reports").select("*").execute()

    if not data.data:
        st.info("No data available")
        return

    st.metric("Total Reports", len(data.data))

    users = set([r["user_email"] for r in data.data])
    st.metric("Total Users", len(users))

    st.subheader("Recent Reports")

    for row in data.data[:10]:
        with st.expander(f"{row['user_email']} - {row['created_at']}"):
            st.write(row["result"])y