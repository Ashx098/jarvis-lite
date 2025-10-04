from fastapi import FastAPI
from pydantic import BaseModel
from agent import Agent


app = FastAPI(
    title="Jarvis‑Lite API",
    description="Local-first AI agent with news, web search, notes, tasks, and RAG capabilities",
    version="0.2"
)
agent = Agent(db_path="jarvis.db")


class Query(BaseModel):
    prompt: str


@app.get("/")
async def root():
    return {
        "message": "Jarvis‑Lite API v0.2",
        "description": "Local-first AI agent with advanced capabilities",
        "endpoints": {
            "/ask": "POST - Query the agent with prompts",
            "/docs": "GET - Interactive API documentation",
            "/health": "GET - Health check"
        },
        "examples": {
            "news": "news: india top headlines today",
            "web_search": "web: what is quantum computing",
            "notes": "note: remember to buy groceries",
            "tasks": "add task: finish project documentation",
            "rag": "ask rag: summarize the research paper",
            "calc": "calc: 2^10 + sqrt(100)"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.2"}


@app.post("/ask")
async def ask(q: Query):
    answer = agent.step(q.prompt)
    return {"answer": answer}
