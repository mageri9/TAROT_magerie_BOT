import html

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message

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
        f'<b>{html.escape(message.from_user.full_name)}</b>, добро пожаловать!',
        reply_markup=card_of_the_day()
                        )
    await message.answer_photo("AgACAgIAAxkDAAIBcmnD_OJrZT4CS-F4jVffIpMX69qaAAIrE2sbVbghSg6_9bNqDP3bAQADAgADeAADOgQ")

@router.message(F.text == '🔮 КАРТА ДНЯ 🔮')
async def card_of_day(message: types.Message):
    """Обработчик кнопки '🔮 КАРТА ДНЯ 🔮'"""
    user_id = message.from_user.id

    card_back = await srv.give_daily_card(user_id)

    if not card_back:
        await message.answer("Вы уже получали карту сегодня.")
        return

    await message.answer_photo(
        card_back,
        caption="Пока не открыли карту, введите что-нибудь. В будущем это на что-то повлияет",
        reply_markup=open_card_button()
                                )

def register_handlers():
    pass