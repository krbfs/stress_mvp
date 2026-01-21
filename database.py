import sqlite3
import json
from datetime import datetime

DB_NAME = "bot_data.db"

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица для опросов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id TEXT UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            questions TEXT NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Таблица для ответов пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            poll_id TEXT NOT NULL,
            answers TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (poll_id) REFERENCES polls(poll_id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_poll(poll_id, title, description, questions, image_url=None):
    """Сохранить опрос в БД"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO polls (poll_id, title, description, questions, image_url)
        VALUES (?, ?, ?, ?, ?)
    """, (poll_id, title, description, json.dumps(questions), image_url))
    
    conn.commit()
    conn.close()

def get_poll(poll_id):
    """Получить опрос по ID"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM polls WHERE poll_id = ?", (poll_id,))
    poll = cursor.fetchone()
    conn.close()
    
    if poll:
        return {
            "id": poll[0],
            "poll_id": poll[1],
            "title": poll[2],
            "description": poll[3],
            "questions": json.loads(poll[4]),
            "image_url": poll[5],
            "created_at": poll[6]
        }
    return None

def save_response(user_id, poll_id, answers):
    """Сохранить ответы пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO responses (user_id, poll_id, answers)
        VALUES (?, ?, ?)
    """, (user_id, poll_id, json.dumps(answers)))
    
    conn.commit()
    conn.close()

def get_responses(poll_id):
    """Получить все ответы для опроса"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, answers, completed_at FROM responses WHERE poll_id = ?
    """, (poll_id,))
    
    responses = cursor.fetchall()
    conn.close()
    
    return [
        {
            "user_id": r[0],
            "answers": json.loads(r[1]),
            "completed_at": r[2]
        }
        for r in responses
    ]

def user_already_responded(user_id, poll_id):
    """Проверить, ответил ли пользователь на опрос"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM responses WHERE user_id = ? AND poll_id = ?
    """, (user_id, poll_id))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0