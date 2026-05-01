   # -------------------------------
    # 🔵 GOOGLE LOGIN (SMART UX FIX)
    # -------------------------------
    st.markdown("### Or login with Google")

    # Step 1 → normal button
    if not st.session_state.get("google_clicked"):

        if st.button("🔵 Continue with Google", key="google_btn"):
            try:
                res = supabase.auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {
                        "redirect_to": REDIRECT_URL
                    }
                })

                if res and res.url:
                    st.session_state.google_url = res.url
                    st.session_state.google_clicked = True
                    st.rerun()

            except Exception as e:
                st.error(f"Google login error: {e}")

    # Step 2 → same button becomes redirect
    else:
        if st.session_state.get("google_url"):
            st.info("Redirecting... click again if not automatic")

            st.markdown(f"""
            <a href="{st.session_state.google_url}" target="_self">
                <button style="
                    width:100%;
                    padding:12px;
                    border-radius:8px;
                    border:1px solid #ccc;
                    background:white;
                    cursor:pointer;
                    font-size:16px;
                ">
                🔵 Continue with Google
                </button>
            </a>
            """, unsafe_allow_html=True)
