import streamlit as st
from supabase_client import supabase

def google_login():
    try:
        res = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "https://ai-oracle-assistant.streamlit.app"
            }
        })

        # ✅ Debug full response
        st.write("DEBUG RESPONSE:", res)

        # ✅ Correct extraction
        if hasattr(res, "url"):
            return res.url
        elif isinstance(res, dict) and "url" in res:
            return res["url"]
        else:
            st.error("OAuth URL not found in response")
            return None

    except Exception as e:
        st.error(f"Google Login Error: {e}")
        return None