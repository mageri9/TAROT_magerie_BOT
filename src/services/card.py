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
    print(f"🔍 give_daily_card: user_id={user_id}")

    if not await can_get_card(user_id):
        print(f"🔍 give_daily_card: user {user_id} already got card today")
        return None, None

    excluded_ids = await get_last_user_cards(user_id, limit=10)
    print(f"🔍 give_daily_card: excluded_ids={excluded_ids}")

    card = await get_random_card(excluded_ids=excluded_ids if excluded_ids else None)
    print(f"🔍 give_daily_card: card={card}")

    if not card:
        print(f"⚠️ give_daily_card: no card found, trying without excluded")
        card = await get_random_card(excluded_ids=None)
        if not card:
            print("❌ Нет карт в колоде!")
            return None, None

    card_id, card_name, card_file_id = card
    print(f"✅ give_daily_card: selected {card_name} (id={card_id})")

    await add_card_to_history(user_id, card_id)
    await save_card_requests(user_id)

    card_back = await get_card_back()
    print(f"🔍 card_back from get_card_back() = {card_back}")  # 👈 добавить
    print(f"🔍 type = {type(card_back)}")  # 👈 добавить
    return card_id, card_back

