from ..crud import can_get_card, save_card_requests, get_card_back

async def give_daily_card(user_id: int) -> str:
    """
    Выдать карту дня.
    Возвращает file_id рубашки, если можно получить карту.
    Если нельзя — возвращает None.
    """
    print("Заглушка в сервисах на карту дня")
    # Временно отключаем проверку
    # if not await can_get_card(user_id):
    #     return None

    await save_card_requests(user_id)
    return await get_card_back()

async def can_get_today_card(user_id: int) -> bool:
    """Обёртка для проверки"""
    return True
    # return await can_get_card(user_id)