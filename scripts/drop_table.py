import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.core.db import db

async def drop_table():
    await db.connect()
    await db.execute('DROP TABLE IF EXISTS tarot_cards')
    print("✅ Таблица tarot_cards удалена")
    await db.close()

if __name__ == '__main__':
    asyncio.run(drop_table())