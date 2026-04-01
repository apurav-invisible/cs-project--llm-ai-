# 🧠 NeuraAI — Personal AI Assistant with Memory

A backend-powered AI assistant built as a CS project, featuring **multi-LLM support**, **user-specific memory**, **session-based authentication**, and a **3-tier knowledge retrieval system**.

---

## 📌 Overview

NeuraAI is a FastAPI-based conversational AI system that lets users chat with an AI that **remembers them**. It uses OpenRouter to route queries across multiple free LLMs, falls back to stored user knowledge, and finally Wikipedia — all in a smart priority chain.

---

## 🚀 Features

- 🔐 **Auth System** — Signup, Login, Logout with SHA-256 hashed passwords and session tokens
- 🤖 **Multi-LLM Support** — Randomly picks from 7 free LLMs via OpenRouter on each session
- 🧠 **User Memory** — Each user has a personal knowledge base stored in Supabase
- 🌐 **3-Tier Fallback** — LLM → User Memory → Wikipedia
- 💾 **Chat History** — All conversations saved per user in Supabase
- 🖥️ **Tkinter GUI** — Dark-themed desktop UI with Login, Signup, and Chat screens
- 🔄 **Hot Reload** — `watcher.py` auto-reloads frontend on file changes during development
- ⚡ **REST API** — Clean FastAPI endpoints for all operations

---

## 🗂️ Project Structure

```
cs-project--llm-ai/
│
├── main.py            # FastAPI app — all routes (signup, login, chat, add_fact, logout)
├── llm_engine.py      # Core AI logic — LLM calls, 3-tier retrieval, knowledge & chat saving
├── auth.py            # Authentication — hashing, sessions, signup/login/logout
├── session_manager.py # Fetches the most recent active session from Supabase
├── supabase_db.py     # Supabase client initialization
├── frontend.py        # Tkinter GUI — Login, Signup, and Chat pages
├── watcher.py         # Hot-reload watcher for frontend during development
├── requirements.txt   # Python dependencies
├── test.py            # Environment variable sanity check
└── .gitignore
```

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI |
| AI / LLM | OpenRouter API (7 free models) |
| Database | Supabase (PostgreSQL) |
| Auth | SHA-256 + UUID session tokens |
| Knowledge Fallback | Wikipedia API |
| Config | python-dotenv |

---

## 🤖 LLM Models Used (via OpenRouter)

One model is randomly selected per session:

- `deepseek/deepseek-chat-v3-0324:free`
- `meta-llama/llama-4-maverick:free`
- `qwen/qwen2.5-vl-3b-instruct:free`
- `mistralai/mistral-small-3.1-24b-instruct:free`
- `cognitivecomputations/dolphin-mistral-24b-venice-edition:free`
- `tngtech/deepseek-r1t2-chimera:free`
- `z-ai/glm-4.5-air:free`

---

## 🔄 How the AI Works (3-Tier Knowledge System)

```
User sends a message
        │
        ▼
 Step 1: Ask LLM (via OpenRouter)
        │
        ├── Confident reply? ──► Return LLM response ✅
        │
        ▼
 Step 2: Check User's Personal Memory (Supabase)
        │
        ├── Match found? ──► Return stored answer 📘
        │
        ▼
 Step 3: Fallback to Wikipedia
        │
        └── Return Wikipedia summary 🌐
```

---

## 🗄️ Supabase Schema

### `knowledge_base`
| Column | Type | Description |
|---|---|---|
| id | UUID | User ID |
| email | text | User email |
| password | text | SHA-256 hashed |
| knowledge | jsonb | Personal Q&A memory |

### `sessions`
| Column | Type | Description |
|---|---|---|
| user_id | UUID | Reference to user |
| session_token | text | Unique hex token |
| is_active | boolean | Session status |
| created_at | timestamp | Auto-generated |

### `DATA`
| Column | Type | Description |
|---|---|---|
| id | UUID | User ID |
| data | jsonb | Array of chat history |

---

## 🛠️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/apurav-invisible/cs-project--llm-ai-.git
cd cs-project--llm-ai-
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file
```env
OPENROUTER_API_KEY=your_openrouter_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Run the Desktop GUI
```bash
python frontend.py
```

> The GUI auto-starts the FastAPI backend internally — no need to run uvicorn separately when using the frontend.

### 6. (Dev only) Run with hot-reload watcher
```bash
python watcher.py
```

### 7. Open API docs
```
http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Register a new user |
| `POST` | `/login` | Login and get session token |
| `POST` | `/chat` | Send a message to NeuraAI |
| `POST` | `/add_fact` | Add a fact to personal memory |
| `POST` | `/logout` | End the current session |

### Example — Chat Request
```json
POST /chat
{
  "session_token": "your_token_here",
  "message": "What is machine learning?"
}
```

### Example — Add Fact
```json
POST /add_fact
{
  "session_token": "your_token_here",
  "question": "my favourite language",
  "answer": "Python"
}
```

---

## 🔐 Authentication Flow

```
Signup ──► SHA-256 hash password ──► Store in Supabase ──► Auto-login ──► Return session token
Login  ──► Verify credentials ──► Deactivate old sessions ──► Create new session token
Logout ──► Mark session as inactive
```

---

## 📦 Requirements

```
fastapi
uvicorn
openai
supabase
wikipedia
python-dotenv
pydantic
requests
tkinter
watchdog
```

---

## 👨‍💻 Author

**Apurav** — CS Project | LLM & AI

---

## 📄 License

This project is for educational purposes as part of a Computer Science project.
