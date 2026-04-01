import os
import json
import wikipedia
from supabase_db import supabase
from dotenv import load_dotenv
from wikipedia.exceptions import DisambiguationError, PageError
from openai import OpenAI
import random

load_dotenv()

user_sessions ={}

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
print(" OpenRouter Key loaded:", bool(OPENROUTER_KEY))

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
        return completion.choices[0].message.content or " Empty LLM response"
    except Exception as e:
        return f" LLM error: {str(e)}"

#ai 

def ai_res(user_id: str, prompt: str):
    if user_id not in user_sessions:
        try:
            row = (
                supabase.table("knowledge_base")
                .select("chats")
                .eq("id", user_id)
                .single()
                .execute()
            )
            chats = row.data.get("chats", []) if row.data else []
        except Exception:
            chats = []

        user_sessions[user_id] = [{"role": "system", "content": "You are NeuraAI, a friendly and reasoning AI assistant. Remember everything said in this chat like a human would."}]
        for msg in chats:
            user_sessions[user_id].append({"role": "user", "content": msg["prompt"]})
            user_sessions[user_id].append({"role": "assistant", "content": msg["response"]})

    
    user_sessions[user_id].append({"role": "user", "content": prompt})

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=user_sessions[user_id],
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f" LLM error: {str(e)}"

    user_sessions[user_id].append({"role": "assistant", "content": reply})

    save(user_id, prompt, reply)

    return f"( Neura) {reply}"



# ---------------- KNOWLEDGE ADD ----------------
def add(user_id: str, question: str, answer: str) -> str:
    row = (
        supabase.table("knowledge_base")
        .select("knowledge", "chats")
        .eq("id", user_id)
        .execute()
    )

    knowledge = row.data.get("knowledge", {}) if row.data else {}
    chats = row.data.get("chats", []) if row.data else []

    knowledge[question.strip()] = answer

    if row.data:
        # Update both knowledge and chats safely
        supabase.table("knowledge_base").update({
            "knowledge": knowledge,
            "chats": chats
        }).eq("id", user_id).execute()
    else:
        # New user record with both fields
        supabase.table("knowledge_base").insert({
            "id": user_id,
            "knowledge": knowledge,
            "chats": []
        }).execute()

    return " Added to your personal knowledge!"


def save(user_id: str, prompt: str, response: str) -> None:

    try:
        result = (
            supabase.table("knowledge_base")
            .select("chats")
            .eq("id", user_id)
            .single()
            .execute()
        )

        data = result.data if isinstance(result.data, dict) else {}
        chats = data.get("chats", []) if data else []

    except Exception as e:
        print(" Load error:", e)
        chats = []
        data = None

    # Append new chat pair
    chats.append({"prompt": prompt, "response": response})
    chats = chats[-50:]

    print(f"Total chats after append: {len(chats)}")

    try:
        if  data != {}:
            res = (
                supabase.table("knowledge_base")
                .update({"chats": chats})
                .eq("id", user_id)
                .execute()
            )
        else:
            res = (
                supabase.table("knowledge_base")
                .insert({
                    "id": user_id,
                    "knowledge": {},
                    "chats": chats,
                })
                .execute()
            )

    except Exception as e:
        print(" Save error:", e)
