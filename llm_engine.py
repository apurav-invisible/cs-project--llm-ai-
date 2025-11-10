import os
import json
import requests
import wikipedia
from supabase_db import supabase
from dotenv import load_dotenv
from wikipedia.exceptions import DisambiguationError, PageError
from openai import OpenAI

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
MODEL = "deepseek/deepseek-chat-v3-0324:free"


client = OpenAI(
  base_url=OPENROUTER_URL,
  api_key=OPENROUTER_KEY,
)


print("🔑 OpenRouter Key loaded:", bool(os.getenv("OPENROUTER_API_KEY")))

# ---------------- LLM CALL ----------------
def ask_llm(prompt: str) -> str:
    if not OPENROUTER_KEY:
        return "⚠️ Missing OPENROUTER_API_KEY in .env"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "NeuraAI Dev"
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are NeuraAI, a helpful conversational assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=30)
    except Exception as e:
        return f"⚠️ Network error: {e}"

    ctype = res.headers.get("Content-Type", "")
    if res.status_code != 200:
        return f"⚠️ HTTP {res.status_code}: {res.text[:200]}"

    if not res.text.strip():
        return "⚠️ LLM returned empty response body (possibly rate-limited or invalid key)."

    try:
        data = res.json()
    except Exception as e:
        snippet = res.text[:200].replace("\n", " ")
        return f"⚠️ JSON decode failed: {e}. Raw: {snippet}"

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return f"⚠️ Unexpected JSON schema: {json.dumps(data)[:200]}"


# ---------------- MAIN AI FLOW ----------------
def ai_res(user_id: str, prompt: str) -> str:
    """
    ✅ Final Neura Brain Flow
    1️⃣ LLM first (reasoning & natural)
    2️⃣ Supabase memory if LLM uncertain
    3️⃣ Wikipedia last (fallback for facts)
    """

    prompt_lower = prompt.lower().strip()

    # 🧠 1️⃣ THINK (LLM first)
    row = supabase.table("knowledge_base").select("knowledge").eq("id", user_id).single().execute()
    knowledge = row.data.get("knowledge", {}) if row.data else {}

    system_prompt = (
        f"You are NeuraAI, a friendly and reasoning AI assistant.\n"
        f"You think like a human and use user memory if needed.\n"
        f"If you truly don't know something, reply clearly like: 'I’m not sure about that.'\n"
        f"User memory: {json.dumps(knowledge)}"
    )

    llm_reply = ask_llm(f"{system_prompt}\nUser: {prompt}")
    llm_lower = llm_reply.lower()

    unsure_patterns = [
        "i'm not sure", "i don’t know", "i dont know",
        "i have no idea", "sorry", "not sure"
    ]

    if not any(p in llm_lower for p in unsure_patterns):
        return f"(🤖 Neura) {llm_reply}"

    # 💾 2️⃣ RECALL (Supabase memory)
    for q, a in knowledge.items():
        if q.lower() in prompt_lower:
            return f"(📘 From your memory) {a}"

    # 🌐 3️⃣ RESEARCH (Wikipedia)
    try:
        summary = wikipedia.summary(prompt, sentences=3)
        if summary:
            return f"(🌐 Wikipedia) {summary}"
    except (DisambiguationError, PageError):
        pass
    except Exception:
        pass

    return f"(🤖 Neura) {llm_reply}"


# ---------------- KNOWLEDGE ADD ----------------
def add(user_id: str, question: str, answer: str) -> str:
    row = supabase.table("knowledge_base").select("knowledge").eq("id", user_id).single().execute()
    knowledge = row.data.get("knowledge", {}) if row.data else {}

    knowledge[question.strip().lower()] = answer

    if row.data:
        supabase.table("knowledge_base").update({"knowledge": knowledge}).eq("id", user_id).execute()
    else:
        supabase.table("knowledge_base").insert({
            "id": user_id,
            "knowledge": knowledge,
            "chats": []
        }).execute()

    return "✅ Added to your personal knowledge!"


# ---------------- CHAT SAVE ----------------
def save(user_id: str, prompt: str, response: str) -> None:
    row = supabase.table("knowledge_base").select("chats").eq("id", user_id).single().execute()
    chats = row.data.get("chats", []) if row.data else []
    chats.append({"prompt": prompt, "response": response})

    supabase.table("knowledge_base").update({"chats": chats}).eq("id", user_id).execute()
