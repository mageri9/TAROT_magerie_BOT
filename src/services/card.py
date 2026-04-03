from ..crud import can_get_card, save_card_requests, get_card_back
from ..crud.tarot import get_random_card


async def give_daily_card(user_id: int):
    """
    Выдать карту дня.
    Возвращает: (card_id, card_back_file_id)
    Если нельзя — возвращает (None, None)
    """
    if not await can_get_card(user_id):
         return None, None

    # Получаем случайную карту из колоды
    card = await get_random_card()
    if not card:
        print("❌ Нет карт в колоде!")
        return None, None

    card_id, card_name, card_file_id = card
    print(f"✅ Выбрана карта: {card_name} (ID={card_id})")

    # Сохраняем факт получения
    await save_card_requests(user_id)

    # Возвращаем ID карты и рубашку
    card_back = await get_card_back()
    print(f"🔍 card_back = {card_back}")
    return card_id, card_back

