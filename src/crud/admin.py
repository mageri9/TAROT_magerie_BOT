from core.db import db
from datetime import date

async def get_total_users() -> int:
    """Получить общее количество пользователей."""
    result = await db.fetchone("SELECT COUNT(*) FROM users")
    return result[0] if result else 0

async def get_new_users_today() -> int:
    """Получить количество пользователей за сегодня."""
    today = date.today().isoformat()
    result = await db.fetchone(
        "SELECT COUNT(*) FROM users WHERE created_at LIKE $1",
        (f"{today}%",)
    )
    return result[0] if result else 0

async def get_active_users_today() -> int:
    today = date.today().isoformat()
    result = await db.fetchone(
        "SELECT COUNT(DISTINCT user_id) FROM user_cards WHERE last_card_date = $1",
        (today,)
    )
    return result[0] if result else 0