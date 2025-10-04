import os, json, sqlite3


class Memory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._migrate()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _migrate(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS long_memory (k TEXT PRIMARY KEY, v TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS conv (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
        conn.commit()
        conn.close()

    def add_conv(self, role: str, content: str):
        conn = self._get_connection()
        conn.execute("INSERT INTO conv(role, content) VALUES (?,?)", (role, content))
        conn.commit()
        conn.close()

    def last_k(self, k=10):
        conn = self._get_connection()
        cur = conn.execute("SELECT role, content FROM conv ORDER BY id DESC LIMIT ?", (k,))
        rows = cur.fetchall()
        conn.close()
        # Fix: Handle empty result set to prevent "list index out of range"
        if not rows:
            return []
        rows = rows[::-1]  # Reverse to get chronological order
        return [{"role": r, "content": c} for (r,c) in rows]

    def set(self, key: str, value: dict):
        conn = self._get_connection()
        conn.execute("REPLACE INTO long_memory(k,v) VALUES (?,?)", (key, json.dumps(value)))
        conn.commit()
        conn.close()

    def get(self, key: str, default=None):
        conn = self._get_connection()
        cur = conn.execute("SELECT v FROM long_memory WHERE k=?", (key,))
        row = cur.fetchone()
        conn.close()
        return json.loads(row[0]) if row else default
