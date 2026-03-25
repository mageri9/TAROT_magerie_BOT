from ..core.db import db
from datetime import datetime

async def init_users_table():
    """Создать таблицу users"""
    await db.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at TEXT NOT NULL
                                                    )
                    ''')

async def get_user(user_id: int):
    """Получить пользователя по ID"""
    return await db.fetchone(
                            'SELECT * FROM users WHERE user_id = ?',
                             (user_id,)
                             )

async def create_user(user_id: int, username: str = None):
    """Создать нового пользователя"""
    return await db.execute(
        'INSERT INTO users (user_id, username, created_at) VALUES (?, ?, ?)',
            (user_id, username, datetime.now().isoformat())
                            )

async def update_username(user_id: int, user_name: str = None):
    """Обновить USERNAME"""
    return await db.execute(
        'UPDATE users SET username = ? WHERE user_id = ?',
        (user_name, user_id,)
    )