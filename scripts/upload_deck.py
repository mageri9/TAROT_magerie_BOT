import json
import asyncio
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot
from aiogram.types import FSInputFile
from src.core.config import Settings
from src.core.db import db
from src.crud import (
    init_tarot_cards_table,
    save_tarot_card,
    get_total_cards_count,
)


def calculate_card_id(card: dict, index: int) -> int:
    """Вычисляет сквозной ID карты от 0 до 77."""
    if card['arcana'] == "Major Arcana":
        return int(card['number'])

    suits_order = ["Cups", "Swords", "Wands", "Pentacles"]
    suit = card['suit']
    suit_offset = suits_order.index(suit) * 14
    number = int(card['number'])
    return 22 + suit_offset + (number - 1)


async def upload_deck():
    """Загрузить колоду из 78 карт в БД"""
    print("🚀 Начинаю загрузку колоды...")

    config = Settings()
    bot = Bot(token=config.BOT_TOKEN)
    await db.connect()

    await init_tarot_cards_table()
    print("✅ Таблица tarot_cards готова")

    json_path = Path("tarot-images.json")
    if not json_path.exists():
        print(f"❌ Файл {json_path} не найден!")
        return

    with open(json_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    cards = data['cards']
    print(f"📖 Найдено {len(cards)} карт в JSON")

    images_path = Path("tarot_images")
    if not images_path.exists():
        print(f"❌ Папка {images_path} не найдена!")
        return

    count = 0
    for idx, card in enumerate(cards):
        img_file = images_path / card['img']

        if not img_file.exists():
            print(f"⚠️ Нет картинки: {card['img']}")
            continue

        card_id = calculate_card_id(card, idx)


        photo = FSInputFile(str(img_file))

        msg = await bot.send_photo(
            chat_id=config.ADMIN_IDS[0],
            photo=photo,
            caption=f"📸 [{card_id}] {card['name']}"
        )

        file_id = msg.photo[-1].file_id

        await save_tarot_card(
            card_id=card_id,
            name=card['name'],
            arcana=card['arcana'],
            suit=card['suit'] if card['suit'] else "Major",
            card_number=card['number'],
            file_id=file_id
        )
        count += 1
        print(f"✅ {count:2d}. ID={card_id:2d} | {card['name']}")

    total = await get_total_cards_count()
    print(f"\n🎉 Готово! В БД {total} карт")

    print("\n📊 Диапазон ID:")
    print("  Старшие Арканы: 0-21")
    print("  Cups: 22-35")
    print("  Swords: 36-49")
    print("  Wands: 50-63")
    print("  Pentacles: 64-77")

    await db.close()
    await bot.session.close()


if __name__ == '__main__':
    asyncio.run(upload_deck())