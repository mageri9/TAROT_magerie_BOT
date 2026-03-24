from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from ...filters.check_admin import IsAdmin

from ...crud.card_back import get_card_back

from ...keyboards.admin import get_admin_keyboard, get_cancel_keyboard


router = Router()

# ==================== FSM состояния ====================
class AdminStates(StatesGroup):
    """Состояния для админ-действий"""
    waiting_for_photo = State()
    waiting_for_save_back = State()

# ==================== Callback handlers ====================

@router.callback_query(F.data == "admin:get_file_id", IsAdmin())
async def get_photo_id_start(callback: CallbackQuery, state: FSMContext):
    """Начало получения file_id"""
    await state.set_state(AdminStates.waiting_for_photo)
    await callback.message.answer(
        "📸 Отправьте фото, чтобы получить его file_id\n\n"
        "После отправки фото вы получите его file_id",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin:save_card_back", IsAdmin())
async def save_card_back_start(callback: CallbackQuery, state: FSMContext):
    """Начало сохранения рубашки"""
    await state.set_state(AdminStates.waiting_for_save_back)
    await callback.message.answer(
        "🃏 Отправьте фото для новой рубашки карт\n\n"
        "После отправки фото рубашка будет сохранена",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "admin:view_card_back", IsAdmin())
async def view_card_back_start(callback: CallbackQuery, state: FSMContext):
    """Просмотр текущей рубашки"""
    file_id = await get_card_back()
    if file_id:
        await callback.message.answer_photo(
            file_id,
            caption="🃏 Текущая рубашка карт.",
            reply_markup=get_admin_keyboard()
        )
    else:
        await callback.message.answer(
            "❌ Рубашка не установлена.",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()

@router.callback_query(F.data == "admin:cancel", IsAdmin())
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Отмена текущего действия"""
    await state.clear()  # очищаем состояние FSM
    await callback.message.edit_text(
        "❌ Действие отменено",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()

def register_handlers():
    """Регистрируем обработчики колбэков админа"""
    pass
