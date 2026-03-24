from ..core.db import db

async def init_card_back():
    """Создает таблицу для хранения рубашки карт"""
    await db.execute('''
    CREATE TABLE IF NOT EXISTS card_back (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    file_id TEXT NOT NULL
        )
                     ''')

    #Проверяем, есть ли запись
    result = await db.fetchone('SELECT id FROM card_back WHERE id = 1')
    if not result:
        await db.execute('''
        INSERT INTO card_back (id, file_id)
        VALUES (1, '')
                         ''')

async def get_card_back() -> str:
    """Получить file_id рубашки"""
    result = await db.fetchone('SELECT file_id FROM card_back WHERE id = 1')
    return result[0] if result else None

async def update_card_back(file_id: str) -> None:
    """Обновить рубашку"""
    await db.execute('''
    UPDATE card_back SET file_id = ? WHERE id = 1
                     ''', (file_id,))
