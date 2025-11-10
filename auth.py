import hashlib
import uuid
import secrets
from supabase_db import supabase

# --- Hash password ---
def hash_pass(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Create new session ---
def create_session(user_id: str):
    token = secrets.token_hex(32)
    supabase.table("sessions").insert({
        "user_id": user_id,
        "session_token": token,
        "is_active": True
    }).execute()
    return token

# --- Validate token ---
def validate_session(token: str):
    session = supabase.table("sessions").select("*").eq("session_token", token).eq("is_active", True).execute()
    if not session.data:
        return None
    return session.data[0]["user_id"]

# --- Signup ---
def signup_user(email: str, password: str):
    hashed = hash_pass(password)
    user_id = str(uuid.uuid4())

    exist = supabase.table("knowledge_base").select("email").eq("email", email).execute()
    if exist.data:
        return {"error": "USER ALREADY EXISTS"}

    supabase.table("knowledge_base").insert({
        "id": user_id,
        "email": email,
        "password": hashed,
        "knowledge": {},
        "chats": []
    }).execute()

    # auto-login after signup
    token = create_session(user_id)
    return {"message": "Account created successfully!", "session_token": token}

# --- Login ---
def login_user(email: str, password: str):
    hashed = hash_pass(password)
    user = supabase.table("knowledge_base").select("*").eq("email", email).eq("password", hashed).execute()

    if not user.data:
        return {"error": "INVALID CREDENTIALS"}

    user_id = user.data[0]["id"]

    # deactivate old sessions
    supabase.table("sessions").update({"is_active": False}).eq("user_id", user_id).execute()

    # create new session
    token = create_session(user_id)
    return {"message": "Login successful", "session_token": token}

# --- Logout ---
def logout_user(token: str):
    supabase.table("sessions").update({"is_active": False}).eq("session_token", token).execute()
    return {"message": "Logged out successfully!"}
