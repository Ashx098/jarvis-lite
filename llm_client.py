import os, json, requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "OLLAMA").upper()
        self.model = os.getenv("MODEL", "llama3.1:8b")
        if self.provider == "OPENAI":
            self.base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.key = os.getenv("OPENAI_API_KEY")
        elif self.provider == "GROQ":
            self.base = "https://api.groq.com/openai/v1"
            self.key = os.getenv("GROQ_API_KEY")
        else: # OLLAMA
            self.base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.key = None

    def chat(self, messages: list[Dict[str, str]], temperature: float = 0.2) -> str:
        url = f"{self.base}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        body = {"model": self.model, "messages": messages, "temperature": temperature}
        r = requests.post(url, headers=headers, data=json.dumps(body), timeout=90)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
