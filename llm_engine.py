import os
import json
import wikipedia
from supabase_db import supabase
from dotenv import load_dotenv
from wikipedia.exceptions import DisambiguationError, PageError
from openai import OpenAI
import random

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1"  # ✅ correct base URL
ALL_MODELS = [
    "deepseek/deepseek-chat-v3-0324:free",
    "meta-llama/llama-4-maverick:free",
    "qwen/qwen2.5-vl-3b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "tngtech/deepseek-r1t2-chimera:free",
    "z-ai/glm-4.5-air:free"
]
MODEL = random.choice(ALL_MODELS)
print("🔑 OpenRouter Key loaded:", bool(OPENROUTER_KEY))

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # ✅ must end at /v1, not /v1/chat/completions
    api_key=OPENROUTER_KEY,
)

# ---------------- LLM CALL ----------------
def ask_llm(messages: list) -> str:
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            extra_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "NeuraAI Dev"
            },
        )
        return completion.choices[0].message.content or "⚠️ Empty LLM response"
    except Exception as e:
        return f"⚠️ LLM error: {str(e)}"


# ---------------- MAIN AI FLOW ----------------
def ai_res(user_id: str, prompt: str):
    # Get user memory
    row = (
        supabase.table("knowledge_base")
        .select("knowledge")
        .eq("id", user_id)
        .single()
        .execute()
    )
    knowledge = row.data.get("knowledge", {}) if row.data else {}

    # Create system context
    system_prompt = (
        "You are NeuraAI, a friendly and reasoning AI assistant.\n"+
        "You think like a human and use user memory if needed.\n"+
        "If you truly don't know something, reply clearly like: 'I m not sure about that.'\n"
        f"User memory: {json.dumps(knowledge)}"
    )

    # Compose messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    # 🧠 Step 1: Ask LLM first
    llm_reply = ask_llm(messages)

    if not llm_reply or not isinstance(llm_reply, str):
        return "(🤖 Neura) ⚠️ No valid response from LLM."

    llm_lower = llm_reply.lower()
    unsure_patterns = ["i'm not sure", "i dont know", "not sure", "no idea", "sorry"]

    # If confident, return LLM reply
    if not any(p in llm_lower for p in unsure_patterns):
        return f"(🤖 Neura) {llm_reply}"

    # 💾 Step 2: Use stored knowledge
    for q, a in knowledge.items():
        if q.lower() in prompt.lower():
            return f"(📘 From your memory) {a}"

    # 🌐 Step 3: Fallback to Wikipedia
    try:
        summary = wikipedia.summary(prompt, sentences=3)
        if summary:
            return f"(🌐 Wikipedia) {summary}"
    except (DisambiguationError, PageError):
        pass
    except Exception:
        pass

    # Final fallback
    return f"(🤖 Neura) {llm_reply}"


# ---------------- KNOWLEDGE ADD ----------------
def add(user_id: str, question: str, answer: str) -> str:
    row = (
        supabase.table("knowledge_base")
        .select("knowledge")
        .eq("id", user_id)
        .single()
        .execute()
    )
    knowledge = row.data.get("knowledge", {}) if row.data else {}

    knowledge[question.strip()] = answer

    if row.data:
        supabase.table("knowledge_base").update({"knowledge": knowledge}).eq("id", user_id).execute()
    else:
        supabase.table("knowledge_base").insert(
            {"id": user_id, "knowledge": knowledge}
        ).execute() and supabase.table("DATA").insert({"data":[]}).execute()

    return "✅ Added to your personal knowledge!"


# ---------------- CHAT SAVE ----------------
def save(user_id: str, prompt: str, response: str) -> None:
    try:
        # Try to fetch existing chat data
        row1 = (
            supabase.table("DATA")
            .select("data")
            .eq("id", user_id)
            .single()
            .execute()
        )
        chats = row1.data.get("data", []) if row1.data else []
    except Exception:
        # If no record exists yet
        chats = []

    # Add the new chat
    chats.append({"prompt": prompt, "response": response})

    # Upsert automatically inserts if no row exists, or updates otherwise
    supabase.table("DATA").upsert({ "data": chats}).execute()
