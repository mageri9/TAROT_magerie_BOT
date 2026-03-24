import html

from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import src.services as repo
import src.keyboards.user as kb
from src.crud.card import can_get_card, save_card_requests

router = Router()


async def start_handler(message: Message):
    await repo.create_user(user_id=message.from_user.id)
    await message.answer(f'<b>{html.escape(message.from_user.full_name)}</b>, добро пожаловать!',
                         reply_markup=kb.start_menu)

    #Обработка сообщения "карта дня"
async def card_of_day(message: types.Message):
    user_id = message.from_user.id

    #Проверяем, можно ли получить карту
    if not await can_get_card(user_id):
        await message.answer("Вы уже получали карту сегодня.")
        return

    # Тут логика получения карты
    await message.answer("🎴 Вот ваша карта дня...")

    #Сохраняем, что пользователь получил карту
    await save_card_requests(user_id)



def register_handlers():
    router.message.register(start_handler, CommandStart())
    router.message.register(card_of_day, F.text == 'КАРТА ДНЯ')