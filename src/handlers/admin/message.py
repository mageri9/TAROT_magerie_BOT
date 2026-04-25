import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from crud.card_back import update_card_back
from filters.check_admin import IsAdmin
from keyboards.admin import get_admin_keyboard, get_cancel_keyboard

from .callback import AdminStates

router = Router()


@router.message(Command("admin"), IsAdmin())
async def admin_handler(message: Message):
    """Вход в админ меню по команде /admin"""
    await message.answer(
        f"Welcome to admin menu, {html.escape(message.from_user.full_name)}",
        reply_markup=get_admin_keyboard(),
    )


# ==================== Message handlers для FSM состояний ====================


@router.message(AdminStates.waiting_for_photo, IsAdmin())
async def handle_photo_for_file_id(message: Message, state: FSMContext):
    """Обработка фото для получения file_id"""
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото", reply_markup=get_cancel_keyboard())
        return

    file_id = message.photo[-1].file_id
    await state.clear()
    await message.answer(
        f"✅ file_id:\n\n<code>{file_id}</code>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@router.message(AdminStates.waiting_for_save_back, IsAdmin())
async def handle_photo_for_save_back(message: Message, state: FSMContext):
    """Обработка фото для сохранения рубашки"""
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото", reply_markup=get_cancel_keyboard())
        return

    file_id = message.photo[-1].file_id
    await update_card_back(file_id)
    await state.clear()
    await message.answer("✅ Рубашка сохранена!", reply_markup=get_admin_keyboard())


def register_handlers():
    """Регистрируем обработчики сообщений админа"""
    pass
