"""
Аналитика кликов и взаимодействий пользователей
"""
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from constants import DB_PATH
from logger import logger

def init_clicks_table():
    """Инициализировать таблицу кликов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            button_name TEXT NOT NULL,
            callback_data TEXT,
            poll_id TEXT,
            question_idx INTEGER,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def log_click(user_id: int, button_name: str, callback_data: str = None, 
              poll_id: str = None, question_idx: int = None):
    """Логировать клик по кнопке"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO clicks (user_id, button_name, callback_data, poll_id, question_idx)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, button_name, callback_data, poll_id, question_idx))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Click logged - User: {user_id}, Button: {button_name}")

def get_total_clicks(poll_id: str = None) -> int:
    """Получить общее количество кликов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if poll_id:
        cursor.execute(
            "SELECT COUNT(*) FROM clicks WHERE poll_id = ?",
            (poll_id,)
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM clicks")
    
    total = cursor.fetchone()[0]
    conn.close()
    
    return total

def get_clicks_by_button(poll_id: str = None) -> dict:
    """Получить количество кликов по каждой кнопке"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if poll_id:
        cursor.execute("""
            SELECT button_name, COUNT(*) as count
            FROM clicks
            WHERE poll_id = ?
            GROUP BY button_name
            ORDER BY count DESC
        """, (poll_id,))
    else:
        cursor.execute("""
            SELECT button_name, COUNT(*) as count
            FROM clicks
            GROUP BY button_name
            ORDER BY count DESC
        """)
    
    results = cursor.fetchall()
    conn.close()
    
    return {button: count for button, count in results}

def get_clicks_by_question(poll_id: str) -> dict:
    """Получить клики по вопросам"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT question_idx, COUNT(*) as count
        FROM clicks
        WHERE poll_id = ? AND question_idx IS NOT NULL
        GROUP BY question_idx
        ORDER BY question_idx
    """, (poll_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return {f"q_{q}": count for q, count in results}

def get_clicks_timeline(poll_id: str = None, days: int = 7) -> list:
    """Получить график кликов по времени"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    if poll_id:
        cursor.execute("""
            SELECT DATE(clicked_at) as date, COUNT(*) as count
            FROM clicks
            WHERE poll_id = ? AND clicked_at >= ?
            GROUP BY DATE(clicked_at)
            ORDER BY date
        """, (poll_id, from_date))
    else:
        cursor.execute("""
            SELECT DATE(clicked_at) as date, COUNT(*) as count
            FROM clicks
            WHERE clicked_at >= ?
            GROUP BY DATE(clicked_at)
            ORDER BY date
        """, (from_date,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"date": date, "clicks": count} for date, count in results]

def get_user_clicks(user_id: int) -> dict:
    """Получить клики пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT button_name, COUNT(*) as count
        FROM clicks
        WHERE user_id = ?
        GROUP BY button_name
    """, (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return {button: count for button, count in results}

def get_most_clicked_buttons(limit: int = 10) -> list:
    """Получить самые кликаемые кнопки"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT button_name, COUNT(*) as count
        FROM clicks
        GROUP BY button_name
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"button": button, "clicks": count} for button, count in results]

def get_click_funnel(poll_id: str) -> dict:
    """Получить воронку (funnel) кликов - где теряются пользователи"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Клики по вопросам
    cursor.execute("""
        SELECT question_idx, COUNT(DISTINCT user_id) as users
        FROM clicks
        WHERE poll_id = ? AND question_idx IS NOT NULL
        GROUP BY question_idx
        ORDER BY question_idx
    """, (poll_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    funnel = {}
    for q_idx, users in results:
        funnel[f"Question {q_idx + 1}"] = users
    
    return funnel

def get_average_clicks_per_user(poll_id: str = None) -> float:
    """Получить среднее количество кликов на пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if poll_id:
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id), COUNT(*)
            FROM clicks
            WHERE poll_id = ?
        """, (poll_id,))
    else:
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id), COUNT(*)
            FROM clicks
        """)
    
    result = cursor.fetchone()
    conn.close()
    
    if result[0] == 0:
        return 0
    
    return round(result[1] / result[0], 2)

def get_click_statistics(poll_id: str = None) -> dict:
    """Получить полную статистику кликов"""
    return {
        "total_clicks": get_total_clicks(poll_id),
        "clicks_by_button": get_clicks_by_button(poll_id),
        "timeline": get_clicks_timeline(poll_id),
        "most_clicked": get_most_clicked_buttons(5),
        "avg_clicks_per_user": get_average_clicks_per_user(poll_id)
    }

def format_click_report(poll_id: str = None) -> str:
    """Отформатировать отчет по кликам"""
    stats = get_click_statistics(poll_id)
    
    report = "📊 АНАЛИТИКА КЛИКОВ\n\n"
    report += f"Всего кликов: {stats['total_clicks']}\n"
    report += f"Среднее кликов на пользователя: {stats['avg_clicks_per_user']}\n\n"
    
    report += "🔘 Топ кнопок:\n"
    for button, count in list(stats['clicks_by_button'].items())[:10]:
        percentage = (count / stats['total_clicks'] * 100) if stats['total_clicks'] > 0 else 0
        report += f"  {button}: {count} ({percentage:.1f}%)\n"
    
    return report

def get_user_engagement(user_id: int) -> dict:
    """Получить вовлеченность пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Количество кликов
    cursor.execute("SELECT COUNT(*) FROM clicks WHERE user_id = ?", (user_id,))
    total_clicks = cursor.fetchone()[0]
    
    # Количество опросов пройденных
    cursor.execute("SELECT COUNT(*) FROM responses WHERE user_id = ?", (user_id,))
    total_polls = cursor.fetchone()[0]
    
    # Первый и последний клик
    cursor.execute("""
        SELECT MIN(clicked_at), MAX(clicked_at) FROM clicks WHERE user_id = ?
    """, (user_id,))
    first_click, last_click = cursor.fetchone()
    
    conn.close()
    
    return {
        "user_id": user_id,
        "total_clicks": total_clicks,
        "total_polls_completed": total_polls,
        "first_click": first_click,
        "last_click": last_click,
        "is_active": total_clicks > 0
    }