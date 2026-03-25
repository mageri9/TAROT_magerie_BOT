from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto


from ...keyboards.user import open_card_actions_keyboard
from ...crud.tarot import get_card_by_id, get_random_card


router = Router()


@router.callback_query(F.data.startswith("open_card"))
async def open_card(callback: CallbackQuery):
    """Открыть карту по ID"""
    # Получаем card_id из callback_data
    parts = callback.data.split(":")
    card_id = int(parts[1]) if len(parts) > 1 else None

    if card_id is not None:
        card = await get_card_by_id(card_id)

        if card:

            _, card_name, card_file_id = card

            await callback.message.edit_media(
                                                InputMediaPhoto(
                                                media=card_file_id,
                                                caption=f"✨ {card_name} ✨\n\nТолкование появится позже...",
                                                                ),
                                            reply_markup=open_card_actions_keyboard(card_id)
                                             )
            await callback.answer(f"✨ {card_name} открыта!")
            return

    # Если card_id нет или карта не найдена
    await callback.answer("❌ Карта не найдена")

@router.callback_query(F.data.startswith("reroll"))
async def reroll_card(callback: CallbackQuery):
    """Другая карта (реролл)"""
    parts = callback.data.split(":")
    old_card_id = int(parts[1]) if len(parts) > 1 else None

    # Получаем новую случайную карту
    card = await get_random_card()
    if not card:
        await callback.answer("❌ Не удалось получить карту")
        return

    card_id, card_name, card_file_id = card

    await callback.message.edit_media(
                                    InputMediaPhoto(
                                    media=card_file_id,
                                    caption=f"✨ {card_name} ✨\n\nТолкование появится позже..."
                                                   ),
                                reply_markup=open_card_actions_keyboard(card_id)
                                     )
    await callback.answer(f"🔄 Новая карта: {card_name}")

@router.callback_query(F.data == "share")
async def share_card(callback: CallbackQuery):
    """Поделиться картой (заглушка)"""
    await callback.answer("📤 Функция поделиться скоро появится!", show_alert=True)


@router.callback_query(F.data == "cancel")
async def cancel_handler(query: CallbackQuery):
    await query.message.edit_text('Operation canceled')


def register_handlers():
    pass
