import streamlit as st

def analyze_page(client, supabase):

    st.title("🔍 Analyze SQL")

    user_email = st.session_state.get("username")

    # =========================
    # FETCH USER DATA
    # =========================
    user_data = supabase.table("users").select("*").eq(
        "email", user_email
    ).execute()

    user = user_data.data[0] if user_data.data else {}

    # ✅ SAFE DEFAULTS
    user_role = user.get("role", "user")
    usage_count = user.get("usage_count") or 0

    # =========================
    # LIMIT FREE USERS
    # =========================
    if user_role == "user" and usage_count >= 5:
        st.error("🚫 Free limit reached. Upgrade to Pro.")
        return

    # =========================
    # UI
    # =========================
    task = st.selectbox("Select Task", ["Query Optimization", "Explain Plan"])

    query = st.text_area("Enter your query:")

    if st.button("Analyze"):

        if not query.strip():
            st.warning("Please enter a query")
            return

        # =========================
        # OPENAI CALL
        # =========================
        with st.spinner("Analyzing..."):

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an Oracle DBA expert."},
                        {"role": "user", "content": query}
                    ]
                )

                result = response.choices[0].message.content

                st.success("✅ Analysis Complete")
                st.write(result)

                # =========================
                # UPDATE USAGE
                # =========================
                if user_role == "user":
                    supabase.table("users").update({
                        "usage_count": usage_count + 1
                    }).eq("email", user_email).execute()

            except Exception as e:
                st.error(f"Error: {e}")