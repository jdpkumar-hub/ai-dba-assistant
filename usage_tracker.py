from auth import supabase


def track_usage(user_email, action):
    try:
        supabase.table("usage_logs").insert({
            "user_email": user_email,
            "action": action
        }).execute()
    except:
        pass