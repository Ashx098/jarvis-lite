import sqlite3


def ensure(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT, created_at DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()


def add(conn, text: str):
    ensure(conn)
    conn.execute("INSERT INTO notes(text) VALUES (?)", (text,))
    conn.commit()
    return {"ok": True}


def find(conn, q: str, limit: int = 10):
    ensure(conn)
    cur = conn.execute("SELECT id, text, created_at FROM notes WHERE text LIKE ? ORDER BY id DESC LIMIT ?", (f"%{q}%", limit))
    return [{"id": i, "text": t, "ts": ts} for (i,t,ts) in cur.fetchall()]