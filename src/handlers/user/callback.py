from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto

import random

from keyboards.user import open_card_actions_keyboard

from crud import get_card_by_id, get_random_card
from crud import update_card_stats

router = Router()

@router.callback_query(F.data.startswith("open_card"))
async def open_card(callback: CallbackQuery):
    """Открыть карту по ID"""
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    card_id = int(parts[1]) if len(parts) > 1 else None

    if card_id is not None:
        card = await get_card_by_id(card_id)
        if card:
            (_, card_name, card_file_id,
             meaning_direct, meaning_reversed,
             detailed_direct, detailed_reversed) = card

            is_reversed = random.choice([True, False])
            await update_card_stats(user_id, is_reversed)

            if is_reversed:
                meaning = meaning_reversed
                position_text = " (перевёрнутая)"
            else:
                meaning = meaning_direct
                position_text = ""

            caption = f"✨ {card_name}{position_text} ✨\n\n{meaning}"

            await callback.message.edit_media(
                                                InputMediaPhoto(
                                                media=card_file_id,
                                                caption=caption,
                                                                ),
                                            reply_markup=open_card_actions_keyboard(card_id)
                                             )
            await callback.answer(f"✨ {card_name}!")
            return

    # Если card_id нет или карта не найдена
    await callback.answer("❌ Карта не найдена")

@router.callback_query(F.data.startswith("reroll"))
async def reroll_card(callback: CallbackQuery):
    """Другая карта (реролл)"""
    card = await get_random_card()
    if not card:
        await callback.answer("❌ Не удалось получить карту")
        return

    card_id, card_name, card_file_id = card

    full_card = await get_card_by_id(card_id)
    if full_card:
        (_, _, _,
         meaning_direct, meaning_reversed,
         detailed_direct, detailed_reversed) = full_card

        is_reversed = random.choice([True, False])

        user_id = callback.from_user.id
        await update_card_stats(user_id, is_reversed)

        if is_reversed:
            meaning = meaning_reversed or "Толкование в разработке"
            position_text = " (перевёрнутая)"
        else:
            meaning = meaning_direct or "Толкование в разработке"
            position_text = ""

        caption = (f"✨ {card_name}{position_text} ✨\n\n"
                   f"{meaning}\n\n"
                   f"✨ Приходите завтра!")
    else:
        caption = f"✨ {card_name} ✨\n\nТолкование в разработке.✨"

    await callback.message.edit_media(
        InputMediaPhoto(media=card_file_id, caption=caption),
        reply_markup=None
    )

    await callback.answer(f" {card_name}!")


@router.callback_query(F.data == "cancel")
async def cancel_handler(query: CallbackQuery):
    await query.message.edit_text('Operation canceled')


def register_handlers():
    pass
