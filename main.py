from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import sqlite3

app = FastAPI()

DB_PATH = "db.sqlite3"

# Используем твой список чекпоинтов
CHECKPOINTS = [
    (10*60, "10 минут", "Уровень кислорода в крови начинает повышаться."),
    (30*60, "30 минут", "Пульс начинает приходить в норму."),
    (60*60, "1 час", "Снижается риск сердечного приступа."),
    (2*60*60, "2 часа", "В организме начинается выведение никотина."),
    (4*60*60, "4 часа", "Давление стабилизируется."),
    (6*60*60, "6 часов", "В организме меньше угарного газа."),
    (8*60*60, "8 часов", "Уровень кислорода в крови полностью нормализуется."),
    (12*60*60, "12 часов", "Организм очищается от никотина наполовину."),
    (16*60*60, "16 часов", "Восстанавливается вкус и обоняние."),
    (20*60*60, "20 часов", "Печень начинает интенсивно выводить токсины."),
    (24*60*60, "1 день", "В крови практически не осталось никотина."),
    (2*24*60*60, "2 дня", "Вкусовые и обонятельные рецепторы начинают восстанавливаться."),
    (3*24*60*60, "3 дня", "Дыхание становится легче, повышается энергия."),
    (4*24*60*60, "4 дня", "Стабилизируется уровень сахара в крови."),
    (5*24*60*60, "5 дней", "Повышается иммунитет."),
    (6*24*60*60, "6 дней", "Становится легче дышать."),
    (7*24*60*60, "1 неделя", "Кашель уменьшается, дыхательные пути восстанавливаются."),
    (10*24*60*60, "10 дней", "Появляется больше энергии, снижается стресс."),
    (14*24*60*60, "2 недели", "Кровообращение улучшается."),
    (21*24*60*60, "3 недели", "Сосуды становятся эластичнее."),
    (30*24*60*60, "1 месяц", "Легкие начинают очищаться более эффективно."),
    (2*30*24*60*60, "2 месяца", "Восстанавливается физическая выносливость."),
    (3*30*24*60*60, "3 месяца", "Исчезает усталость, кожа выглядит здоровее."),
    (6*30*24*60*60, "6 месяцев", "Почти исчезает одышка."),
    (9*30*24*60*60, "9 месяцев", "Исчезает кашель и проблемы с дыханием."),
    (365*24*60*60, "1 год", "Риск инфаркта снижается в 2 раза."),
]

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

@app.get("/achievements/{user_id}")
async def get_achievements(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT started_at FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    if not row or not row[0]:
        return JSONResponse({"achievements": []})

    started_at = datetime.fromisoformat(row[0])
    now = datetime.utcnow()
    elapsed = (now - started_at).total_seconds()
    result = []

    for seconds, label, description in CHECKPOINTS:
        result.append({
            "label": label,
            "description": description,
            "seconds": seconds,
            "achieved": elapsed >= seconds
        })

    return JSONResponse({"achievements": result})
