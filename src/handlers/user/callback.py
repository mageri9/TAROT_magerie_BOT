import random

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup

from loguru import logger

from keyboards.user import oracle_only_keyboard

from services import ask_oracle

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
                position_text = " 🎴перевёрнутая "
            else:
                meaning = meaning_direct
                position_text = "🃏"

            caption = f"✨ {card_name}{position_text} ✨\n\n{meaning}"

            await callback.message.edit_media(
                                            InputMediaPhoto(media=card_file_id, caption=caption,),
                                            reply_markup=oracle_only_keyboard(card_id)
                                             )
            await callback.answer(f"✨ {card_name}!")
            return

    await callback.answer("❌ Карта не найдена")



# =====================================================================
# 🔄 REROLL — ВРЕМЕННО ОТКЛЮЧЕН (Релиз 1.5)
#    Хендлер сохранён для будущих релизов.
#    Клавиатура переключена на oracle_only_keyboard в open_card.
#    Чтобы вернуть: заменить клавиатуру обратно.

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
            position_text = " 🃏перевёрнутая "
        else:
            meaning = meaning_direct or "Толкование в разработке"
            position_text = "🃏"

        caption = (f"✨ {card_name}{position_text} ✨\n\n"
                   f"{meaning}\n\n"
                   f"✨ Приходите завтра!")
    else:
        caption = f"✨ {card_name} ✨\n\nТолкование в разработке.✨"

    await callback.message.edit_media(
        InputMediaPhoto(media=card_file_id, caption=caption),
        reply_markup=oracle_only_keyboard(card_id)
    )

    await callback.answer(f" {card_name}!")
# =====================================================================


@router.callback_query(F.data.startswith("oracle:"))
async def ask_oracle_handler(callback: CallbackQuery, state: FSMContext):
    """Спросить Оракула о карте."""
    card_id = int(callback.data.split(":")[1])

    card = await get_card_by_id(card_id)
    if not card:
        await callback.answer("❌ Карта не найдена")
        return

    card_name = card[1]

    caption = callback.message.caption or "🃏"
    is_reversed = " 🎴перевёрнутая " in caption
    if is_reversed:
        db_meaning = card[5]  # meaning_reversed
    else:
        db_meaning = card[4]  # meaning_direct

    redis_client = callback.bot.custom.get("redis_client")

    user_id = callback.from_user.id
    context = None
    if redis_client:
        context = await redis_client.get(f"context:{user_id}")

    await state.clear()

    await callback.answer("🔮 Оракул думает...")
    msg = await callback.message.answer("🔮 Спрашиваю у звёзд...")
    logger.info(f"Calling ask_oracle for: {card_name}")

    oracle_answer = await ask_oracle(
        card_name=card_name,
        is_reversed=is_reversed,
        context=context,
        db_meaning=db_meaning,
        redis_client=redis_client
    )

    await msg.edit_text(

        f"🔮 Оракул говорит:\n\n"
        f"{oracle_answer}"
    )
    current_markup = callback.message.reply_markup
    new_markup = None
    if current_markup:
        new_rows = []
        for row in current_markup.inline_keyboard:
            new_buttons = [btn for btn in row if not btn.callback_data.startswith("oracle:")]
            if new_buttons:
                new_rows.append(new_buttons)
        if new_rows:
            new_markup = InlineKeyboardMarkup(inline_keyboard=new_rows)

    await callback.message.edit_reply_markup(reply_markup=new_markup)


def register_handlers():
    pass
