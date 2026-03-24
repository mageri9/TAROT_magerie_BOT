import html

from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message

import src.services as repo
from ...keyboards.user import open_card_button, card_of_the_day
from src.crud.card import save_card_requests
from src.crud.card_back import get_card_back

router = Router()


async def start_handler(message: Message):
    await repo.create_user(user_id=message.from_user.id)
    await message.answer(f'<b>{html.escape(message.from_user.full_name)}</b>, добро пожаловать!',
                         reply_markup=card_of_the_day())

    #Обработка сообщения "карта дня"
async def card_of_day(message: types.Message):
    user_id = message.from_user.id

    print("Заглушка на хэндлер.юзер.месседж ДЛЯ ПОВТОРНОГО ПРИМЕНЕНИЯ")
    #Проверяем, можно ли получить карту
#    if not await can_get_card(user_id):
#        await message.answer("Вы уже получали карту сегодня.")
#        return

    # Тут логика получения карты
    card_back = await get_card_back()
    await message.answer_photo(card_back,
                               caption="Пока не открыли карту, введите что-нибудь. В будущем это на что-то повлияет",
                               reply_markup=open_card_button())

    #Сохраняем, что пользователь получил карту
    await save_card_requests(user_id)





def register_handlers():
    router.message.register(start_handler, CommandStart())
    router.message.register(card_of_day, F.text == '🔮 КАРТА ДНЯ 🔮')