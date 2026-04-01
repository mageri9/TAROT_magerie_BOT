from ..core.db import db

async def init_card_back_table():
    """Создает таблицу для хранения рубашки карт"""
    await db.execute('''
                        CREATE TABLE IF NOT EXISTS card_back (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        file_id TEXT NOT NULL
                                                             )                                                        
                     ''')

async def add_card_back(file_id: str) -> None:
    """Добавить новую рубашку"""
    await db.execute('''
                    INSERT INTO card_back (file_id) VALUES ($1)
                     ''', (file_id,))

async def get_random_card_back() -> None:
    """Получить случайную рубашку"""
    result = await db.fetchone('''
      SELECT file_id FROM card_back ORDER BY RANDOM() LIMIT 1
                               ''')
    return result[0] if result else None

async def get_all_card_backs():
    """Получить все рубашки"""
    return await db.fetchall('SELECT id, file_id FROM card_back')

async def delete_card_back(file_id: int) -> None:
    """Удалить рубашку"""
    await db.execute('DELETE FROM card_back WHERE id = $1', (file_id,))



async def get_card_back() -> str:
    """Получить случайную рубашку (алиас)"""
    return await get_random_card_back()

async def update_card_back(file_id: str) -> None:
    """Добавить рубашку (алиас)"""
    await add_card_back(file_id)
