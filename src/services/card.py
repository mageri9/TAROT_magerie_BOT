from ..crud import (
    can_get_card,
    save_card_requests,
    get_card_back,
    get_last_user_cards,
    add_card_to_history,
    get_random_card
)


async def give_daily_card(user_id: int):
    """Выдать карту дня."""

    if not await can_get_card(user_id):
        return None, None

    excluded_ids = await get_last_user_cards(user_id, limit=10)

    card = await get_random_card(excluded_ids=excluded_ids if excluded_ids else None)

    if not card:
        card = await get_random_card(excluded_ids=None)
        if not card:
            print("❌ Нет карт в колоде!")
            return None, None

    card_id, card_name, card_file_id = card

    await add_card_to_history(user_id, card_id)
    await save_card_requests(user_id)

    card_back = await get_card_back()
    return card_id, card_back

