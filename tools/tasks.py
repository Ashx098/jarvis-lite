import sqlite3


def ensure(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, text TEXT, done INTEGER DEFAULT 0, created_at DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()


def add(conn, text: str):
    ensure(conn)
    conn.execute("INSERT INTO tasks(text) VALUES (?)", (text,))
    conn.commit()
    return {"ok": True}




def list_tasks(conn, only_open=True):
    ensure(conn)
    q = "SELECT id,text,done,created_at FROM tasks WHERE done=0 ORDER BY id DESC" if only_open else "SELECT id,text,done,created_at FROM tasks ORDER BY id DESC"
    cur = conn.execute(q)
    return [{"id": i, "text": t, "done": d==1, "ts": ts} for (i,t,d,ts) in cur.fetchall()]




def mark_done(conn, task_id: int):
    ensure(conn)
    conn.execute("UPDATE tasks SET done=1 WHERE id=?", (task_id,))
    conn.commit()
    return {"ok": True}