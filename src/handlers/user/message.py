import html

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.crud import get_user_stats

import src.services as srv

from ...keyboards.user import open_card_button, card_of_the_day


router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    """Обработчик команды старт"""
    await srv.register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
    )
    await message.answer(
        f'<b>{html.escape(message.from_user.full_name)}</b>, добро пожаловать!\n'
        f'Я бот-предсказатель.\n'
        f'Вам доступна ✨ КАРТА ДНЯ ✨',
        reply_markup=card_of_the_day()
                        )

@router.message(F.text == '🔮 КАРТА ДНЯ 🔮')
async def card_of_day(message: types.Message):
    """Обработчик кнопки '🔮 КАРТА ДНЯ 🔮'"""
    user_id = message.from_user.id

    card_id, card_back = await srv.give_daily_card(user_id)

    if not card_back:
        await message.answer("Вы уже получали карту сегодня.\n"
                             "Приходите завтра!")
        return

    await message.answer_photo(
        card_back,
        caption="🔮 Пока не открыли карту, тщательно сформулируйте вопрос в голове.",
        reply_markup=open_card_button(card_id)
                                )

@router.message(F.text == "📜 ПРОФИЛЬ 📜")
async def profile(message: Message):
    """Статистика пользователя (кнопка)"""
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)

    if not stats or stats[0] == 0:
        await message.answer("🔮 Откройте одну карту.")
        return

    total, upright, reversed_ = stats

    text = f"""
    
    📜 Всего значений: {total}/156
    🃏: {upright}
    🎴: {reversed_}
            """
    await message.answer(text)
    
def register_handlers():
    pass