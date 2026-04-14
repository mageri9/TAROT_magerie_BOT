from core.db import db
from datetime import date

async def init_daily_cards_table():
    """Создает таблицу для карт дня"""
    await db.execute('''
        CREATE TABLE IF NOT EXISTS user_cards (
            user_id BIGINT PRIMARY KEY,
            last_card_date TEXT NOT NULL,
            total_cards INTEGER DEFAULT 0,
            upright_count INTEGER DEFAULT 0,
            reversed_count INTEGER DEFAULT 0
        )
    ''')

async def update_card_stats(user_id: int, is_reversed: bool) -> None:
    """Обновить статистику пользователя после открытия карты"""
    if is_reversed:
        await db.execute(
            "UPDATE user_cards SET total_cards = total_cards + 1, reversed_count = reversed_count + 1"
            " WHERE user_id = $1",
            (user_id,)
        )
    else:
        await db.execute(
            "UPDATE user_cards SET total_cards = total_cards + 1, upright_count = upright_count + 1"
            " WHERE user_id = $1",
            (user_id,)
        )

async def get_user_stats(user_id: int) -> tuple | None:
    """Получить статистику пользователя"""
    return await db.fetchone(
        "SELECT total_cards, upright_count, reversed_count FROM user_cards WHERE user_id = $1",
        (user_id,)
    )


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

# ========== История карт пользователя (для исключения повторов) ==========

async def init_user_card_history_table() -> None:
    """Создать таблицу истории карт пользователя"""
    await db.execute('''
    CREATE TABLE IF NOT EXISTS user_card_history (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        card_id INTEGER NOT NULL,
        opened_at TIMESTAMP DEFAULT NOW()
        )                 
    ''')
    await db.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_card_history_user_id
        ON user_card_history (user_id, opened_at DESC)
    ''')


async def get_last_user_cards(user_id: int, limit: int = 10) -> list[int]:
    """Получить последние N карт пользователя (только ID)"""

    rows = await db.fetchall(
        "SELECT card_id FROM user_card_history "
        "WHERE user_id = $1 ORDER BY opened_at DESC LIMIT $2",
        (user_id, limit)
    )

    result = [row["card_id"] for row in rows]
    return result


async def add_card_to_history(user_id: int, card_id: int) -> None:
    """Добавить карту в историю"""

    await db.execute(
        "INSERT INTO user_card_history (user_id, card_id) VALUES ($1, $2)",
        (user_id, card_id)
    )
