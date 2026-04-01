from ..core.db import db
from datetime import date

async def init_daily_cards_table():
    """Создает таблицу для карт дня"""
    await db.execute('''
        CREATE TABLE IF NOT EXISTS user_cards (
            user_id INTEGER PRIMARY KEY,
            last_card_date TEXT NOT NULL
        )
    ''')

async def can_get_card(user_id: int) -> bool:
    """Проверяет, получал ли пользователь карту сегодня"""
    today = date.today().isoformat()
    result = await db.fetchone(
        'SELECT last_card_date FROM user_cards WHERE user_id = $1',
        (user_id,)
                              )
    if not result:
        return True
    return result[0] != today


async def save_card_requests(user_id: int) -> None:
    """Сохраняет, что пользователь получил карту сегодня"""
    today = date.today().isoformat()
    await db.execute('''
        INSERT INTO user_cards (user_id, last_card_date)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET
            last_card_date = EXCLUDED.last_card_date 
    ''', (user_id, today))