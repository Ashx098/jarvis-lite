import json
SYSTEM = (
"You are a planning layer. Decide the NEXT ACTION as JSON. "
"Allowed tools: news_query, web_search, notes_add, notes_find, task_add, task_list, task_done, rag_query, python_calc, final. "
"Return strictly JSON: {\"tool\": str, \"args\": {..}, \"thought\": str}. If finished, use tool=final with answer."
)


def build_messages(history: list[dict], user_input: str):
    msgs = [{"role": "system", "content": SYSTEM}]
    msgs += history
    msgs.append({"role": "user", "content": user_input})
    return msgs


def parse_plan(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        # Improved fallback: check for RAG intent
        text_lower = text.lower()
        if "ask rag:" in text_lower or "rag" in text_lower:
            return {"tool": "rag_query", "args": {"query": text}, "thought": "fallback to rag"}
        elif "news" in text_lower:
            return {"tool": "news_query", "args": {"query": text}, "thought": "fallback to news"}
        elif "note" in text_lower or "add" in text_lower:
            return {"tool": "notes_add", "args": {"text": text}, "thought": "fallback to notes"}
        elif "task" in text_lower:
            return {"tool": "task_add", "args": {"text": text}, "thought": "fallback to tasks"}
        elif "calc" in text_lower or any(op in text for op in ['+', '-', '*', '/', '(', ')', '%']):
            return {"tool": "python_calc", "args": {"expr": text}, "thought": "fallback to calc"}
        else:
            return {"tool": "web_search", "args": {"query": text[:128]}, "thought": "fallback to web"}
