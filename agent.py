import os, json, sqlite3
from llm_client import LLMClient
from planner import build_messages, parse_plan
from memory import Memory
from tools import web_search, notes, tasks, rag, python_tool
from tools import news as news_tool

class Agent:
    def __init__(self, db_path: str):
        self.mem = Memory(db_path)
        self.llm = LLMClient()
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _llm(self, messages):
        return self.llm.chat(messages)

    def step(self, user_input: str) -> str:
        history = self.mem.last_k(8)
        plan_msg = self.llm.chat(build_messages(history, user_input))
        plan = parse_plan(plan_msg)
        tool = plan.get("tool", "final")
        args = plan.get("args", {})

        obs = None
        if tool == "news_query":
            q = args.get("query") or user_input
            bundle = news_tool.news_bundle(q, llm_call=self._llm)
            obs = bundle
        elif tool == "web_search":
            q = args.get("query") or user_input
            results = web_search.search(q, 4)
            # fetch top1 text
            content = web_search.fetch_clean(results[0]["href"]) if results else ""
            obs = {"results": results, "content": content[:1200]}
        elif tool == "notes_add":
            conn = self._get_connection()
            obs = notes.add(conn, args.get("text", user_input))
            conn.close()
        elif tool == "notes_find":
            conn = self._get_connection()
            obs = notes.find(conn, args.get("query", ""))
            conn.close()
        elif tool == "task_add":
            conn = self._get_connection()
            obs = tasks.add(conn, args.get("text", user_input))
            conn.close()
        elif tool == "task_list":
            conn = self._get_connection()
            obs = tasks.list_tasks(conn, True)
            conn.close()
        elif tool == "task_done":
            conn = self._get_connection()
            obs = tasks.mark_done(conn, int(args.get("id", 0)))
            conn.close()
        elif tool == "rag_query":
            hits = rag.query_for_agent(args.get("query", user_input))
            obs = {"chunks": hits}
        elif tool == "python_calc":
            try:
                obs = {"result": python_tool.calc(args.get("expr", "0"))}
            except Exception as e:
                obs = {"error": str(e)}
        elif tool == "final":
            answer = args.get("answer") or plan.get("thought") or "Done."
            self.mem.add_conv("user", user_input)
            self.mem.add_conv("assistant", answer)
            return answer
        else:
            obs = {"error": f"unknown tool {tool}"}

        # Reflect with observation
        reflect_msgs = [
            {"role": "system", "content": "Craft a factual answer with a short digest and bullet citations (URLs)."},
            {"role": "user", "content": f"User asked: {user_input}\nObservation: {json.dumps(obs)[:4000]}"}
        ]
        answer = self.llm.chat(reflect_msgs)
        self.mem.add_conv("user", user_input)
        self.mem.add_conv("assistant", answer)
        return answer
