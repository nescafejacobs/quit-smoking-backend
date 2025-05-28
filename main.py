from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import sqlite3

app = FastAPI()

DB_PATH = "db.sqlite3"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                started_at TEXT,
                checkpoints TEXT
            )
        """)
        conn.commit()

init_db()

@app.post("/start")
async def start_timer(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO users (user_id, started_at, checkpoints) VALUES (?, ?, ?)", (user_id, now, ""))
        conn.commit()
    return JSONResponse({"ok": True, "started_at": now})

@app.post("/reset")
async def reset_timer(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET started_at = ?, checkpoints = ? WHERE user_id = ?", (now, "", user_id))
        conn.commit()
    return JSONResponse({"ok": True, "started_at": now})

@app.get("/timer/{user_id}")
async def get_timer(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT started_at FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    if not row or not row[0]:
        return JSONResponse({"started_at": None, "elapsed": None})
    started_at = datetime.fromisoformat(row[0])
    now = datetime.utcnow()
    elapsed = now - started_at
    return JSONResponse({
        "started_at": started_at.isoformat(),
        "elapsed": int(elapsed.total_seconds())
    })
