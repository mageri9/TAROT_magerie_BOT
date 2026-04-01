from ..core.db import db

async def init_tarot_cards_table():
    """Создать таблицу колоды"""
    await db.execute('''
        CREATE TABLE IF NOT EXISTS tarot_cards (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            arcana TEXT,
            suit TEXT,
            card_number TEXT,
            file_id TEXT,
            description TEXT,
            meaning_direct TEXT,
            meaning_reversed TEXT,
            detailed_direct TEXT,
            detailed_reversed TEXT
                                               )
                    ''')

async def save_tarot_card(card_id: int, name: str, arcana: str, suit: str, card_number: str, file_id: str):
    """Сохранить карту в БД"""
    await db.execute('''
        INSERT INTO tarot_cards (id, name, arcana, suit, card_number, file_id, description)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
                     ''', (card_id, name, arcana, suit, card_number, file_id, None)
                     )

async def get_random_card():
    """Получить случайную карту из колоды"""
    return await db.fetchone('''
        SELECT id, name, file_id FROM tarot_cards ORDER BY RANDOM() LIMIT 1
                             ''')

async def get_card_by_id(card_id: int):
    """Получить карту по ID"""
    return await db.fetchone('''
        SELECT id, name, file_id,
        meaning_direct, meaning_reversed,
        detailed_direct, detailed_reversed
        FROM tarot_cards WHERE id = $1
                             ''', (card_id,))

async def get_total_cards_count() -> int:
    """Сколько карт в колоде"""
    result = await db.fetchone('SELECT COUNT(*) FROM tarot_cards')
    return result[0] if result else 0