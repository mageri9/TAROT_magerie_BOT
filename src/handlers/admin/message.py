
import html

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from ...filters.check_admin import IsAdmin

from ...crud.card_back import update_card_back, get_card_back
from ...keyboards.admin import get_admin_keyboard


router = Router()


async def admin_handler(message: Message):
    await message.answer(f'Welcome to admin menu, {html.escape(message.from_user.full_name)}',

                         reply_markup=get_admin_keyboard()
                         )

async def get_photo_id(message: Message):
    """Получить file_id картинки"""
    if message.photo:
        file_id = message.photo[-1].file_id
        await message.answer(f"✅ file_id:\n\n<code>{file_id}</code>", parse_mode="HTML")
    else:
        await message.answer("Сначала отправьте фото, затем нажмите кнопку.")

async def save_card_back(message: Message):
    """Сохранить рубашку карт"""
    if message.photo:
        file_id = message.photo[-1].file_id
        await update_card_back(file_id)
        await message.answer("✅ Рубашка сохранена!")
    else:
        await message.answer("Сначала отправьте фото, затем нажмите кнопку.")

async def view_card_back(message: Message):
    """Посмотреть текущую рубашку"""
    file_id = await get_card_back()
    if file_id:
        await message.answer_photo(file_id, caption="🃏 Текущая рубашка карт.")
    else:
        await message.answer("Рубашка не установлена.")



def register_handlers():
    router.message.register(get_photo_id, F.text == "📸 Получить file_id", IsAdmin())
    router.message.register(save_card_back, F.text == "🃏 Сохранить рубашку", IsAdmin())
    router.message.register(view_card_back, F.text == "👁️ Посмотреть рубашку", IsAdmin())
    router.message.register(admin_handler, Command('admin'), IsAdmin())


