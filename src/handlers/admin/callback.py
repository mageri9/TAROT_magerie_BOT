from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery



from ...filters.check_admin import IsAdmin
from ...crud.card_back import get_all_card_backs, delete_card_back
from ...keyboards.admin import get_admin_keyboard, get_cancel_keyboard, get_delete_back_keyboard

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
    print("1. Хэндлер вызван")
    await state.set_state(AdminStates.waiting_for_save_back)
    print("2. Состояние установлено")
    await callback.message.answer(
        "🃏 Отправьте фото для новой рубашки карт\n\n"
        "После отправки фото рубашка будет сохранена",
        reply_markup=get_cancel_keyboard()
    )
    print("3. Сообщение отправлено")
    await callback.answer()
    print("4. Callback answered")

@router.callback_query(F.data == "admin:view_card_back", IsAdmin())
async def view_card_backs(callback: CallbackQuery):
    """Показать все рубашки"""
    backs = await get_all_card_backs()

    if not backs:
        await callback.message.answer("❌ Рубашек пока нет")
        await callback.answer()
        return

    for back in backs:
        await callback.message.answer_photo(
            back[1],
            caption=f"🃏 Рубашка ID: {back[0]}",
            reply_markup=get_delete_back_keyboard(back[0])
        )

    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_back:"), IsAdmin())
async def del_back(callback: CallbackQuery):
    """Удалить рубашку"""
    back_id = int(callback.data.split(":")[2])
    await delete_card_back(back_id)
    await callback.message.edit_caption(caption="✅ Рубашка удалена")
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


@router.callback_query(F.data == "admin:exit", IsAdmin())
async def exit_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Выход из админ-панели"""
    await state.clear()  # очищаем состояние FSM

    # Удаляем сообщение с админ-меню
    await callback.message.delete()

    # Отправляем новое сообщение о выходе
    await callback.message.answer(
        "👋 Вы вышли из админ-панели\n"
        "Для входа используйте /admin"
    )

    # Закрываем callback
    await callback.answer()

def register_handlers():
    """Регистрируем обработчики колбэков админа"""
    pass
