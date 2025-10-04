# Jarvis‑Lite: End‑to‑End Useful AI Agent (v0.2)

A practical, local‑first agent you can run on **Kaarya** today. Focus: notes, tasks, web answers, news, and local RAG over a folder. Pluggable LLM: **Ollama (default)**, **OpenAI**, or **Groq**.

---

## ✨ Capabilities (v0.1 → v0.2)

* **Ask & act loop** (ReAct‑style): plan → use tools → reflect → answer.
* **Tools**

  * `web_search`: DuckDuckGo instant answers + web pages (no paid key).
  * `news`: **NEW** multi‑source headlines + summaries with optional NewsAPI/GNews fallback, retries, and credibility weighting.
  * `notes`: append/grep notes (SQLite).
  * `tasks`: add/list/done (SQLite).
  * `rag`: ask questions over your local `knowledge/` PDFs & docs (Chroma + sentence‑transformers).
  * `python`: safe eval for quick calculations (sandboxed, deny imports by default).
* **Memory**

  * Short‑term: conversation buffer.
  * Long‑term: tool outcomes + user prefs in SQLite.
* **Interfaces**

  * CLI (`python main.py`)
  * REST API (`uvicorn api_server:app`)

> v0.2 goal: be **actually useful daily** with reliable news access and < 15 min setup.

---

## 📁 Repo Structure

```
jarvis-lite/
├─ main.py                    # CLI agent
├─ agent.py                   # Reason → act loop
├─ planner.py                 # Tool selection prompt & parsing
├─ memory.py                  # Short/long memory (SQLite)
├─ llm_client.py              # Ollama/OpenAI/Groq via one interface
├─ tools/
│  ├─ web_search.py
│  ├─ news.py                 # NEW: Advanced news tool
│  ├─ notes.py
│  ├─ tasks.py
│  ├─ rag.py
│  └─ python_tool.py
├─ rag_index.py               # Build/refresh local vector index
├─ api_server.py              # FastAPI for programmatic use
├─ requirements.txt
├─ .env.example
├─ README.md
└─ knowledge/                 # Put your PDFs/markdown here
```

---

## 🔧 Installation

```bash
# 1) Create venv
python -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Copy env and edit
cp .env.example .env
# choose provider: OLLAMA / OPENAI / GROQ

# 4) (Optional) Build RAG index over ./knowledge
python rag_index.py --rebuild

# 5) Run CLI
python main.py

# Or run API
uvicorn api_server:app --reload --port 8000
```

---

## 🧪 Quick Demo

```
> add task: email Saheb the loss curves by 6pm
> note: BRAGS ideas – try multi‑objective BO
> web: best cycle routes in Bangalore Koramangala 10km
> news: india top headlines today
> news: latest ai policy india
> ask rag: what did my MailGuard paper claim about privacy?
> calc: (15% CAGR SIP on 80k for 36 months)
```

---

## 🔐 .env.example

```dotenv
# LLM PROVIDER: OLLAMA | OPENAI | GROQ
LLM_PROVIDER=OLLAMA
MODEL=llama3.1:8b

# If using OpenAI compatible server
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# If using Groq
GROQ_API_KEY=grq-...

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434/v1

# RAG settings
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DIR=.chroma

# SQLite
DB_PATH=jarvis.db

# NEWS (optional)
USE_NEWS_API=false
NEWS_API_PROVIDER=GNEWS   # GNEWS | NEWSAPI | NONE
NEWS_API_KEY=             # get from gnews.io or newsapi.org
NEWS_COUNTRY=in           # default region for headlines
```

---

## 🚀 v0.2 New Features

### Advanced News Tool
- **Multi-source headlines** with credibility weighting
- **API Integration**: Supports GNews and NewsAPI as fallbacks
- **Retry Logic**: Uses tenacity for robust fetching
- **Credibility Scoring**: Trust scores for major news sources
- **Multi-fetch Strategy**: Fetches from top 3 sources instead of just 1
- **Hierarchical Summarization**: Processes content in chunks for better analysis

### Enhanced Reliability
- **Better Error Handling**: Graceful fallbacks when content fetching fails
- **Source Diversity**: Multiple news sources with credibility scores
- **Robust Architecture**: Retry logic and timeout handling

---

## 🛣️ Roadmap (v0.2 → v0.3)

* v0.3: Gmail/Calendar adapters (read‑only), voice I/O (VAD + TTS), cronable digests.
* v0.4: Multi‑agent roles (Researcher/Planner/Executor), better eval (Hallucination checks), guardrails.

---

## Extend
Add a tool in `tools/`, register branch in `agent.step()` and add to planner prompt.
