from loguru import logger
from ..crud import (
    init_users_table,
    init_card_back_table,
    init_daily_cards_table,
    init_tarot_cards_table,
                    )

async def init_all_tables():
    """Инициализирует все таблицы в правильном порядке"""

    tables = [
        ("users", init_users_table),
        ("user_cards", init_daily_cards_table),
        ("card_back", init_card_back_table),
        ("tarot_cards", init_tarot_cards_table),
    ]

    for table_name, init_func in tables:
        try:
            await init_func()
            logger.info(f"✅ Таблица '{table_name}' готова")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании таблицы '{table_name}': {e}")
            raise
    logger.info("🎉 Все таблицы инициализированы")