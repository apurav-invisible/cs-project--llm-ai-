from supabase_db import supabase

def get_active_user():
    """Return the user_id of the most recent active session."""
    res = supabase.table("sessions") \
        .select("user_id") \
        .eq("is_active", True) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
    if res.data:
        return res.data[0]["user_id"]
    return None