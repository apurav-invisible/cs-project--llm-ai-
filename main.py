from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_engine import ai_res, save, add
from auth import signup_user, login_user, logout_user, validate_session
from session_manager import get_active_user

app = FastAPI(title="NeuraAI")

class Auth(BaseModel):
    email: str
    password: str

class Chat(BaseModel):
    session_token: str
    message: str

class Fact(BaseModel):
    session_token: str
    question: str
    answer: str

# --- Signup ---
@app.post("/signup")
def signup(req: Auth):
    res = signup_user(req.email, req.password)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# --- Login ---
@app.post("/login")
def login(req: Auth):
    res = login_user(req.email, req.password)
    if "error" in res:
        raise HTTPException(status_code=401, detail=res["error"])
    return res


# --- Chat ---
@app.post("/chat")
def chat(req: Chat):
    user_id = get_active_user()
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    reply = ai_res(user_id, req.message)
    save(user_id, req.message, reply)
    return {"reply": reply}

# --- Add Fact ---
@app.post("/add_fact")
def add_fact(req: Fact):
    user_id = get_active_user()
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")

    add(user_id, req.question, req.answer)
    return {"message": "Fact added successfully"}

# --- Logout ---
@app.post("/logout")
def logout(req: Chat):
    return logout_user(req.session_token)
