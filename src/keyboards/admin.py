from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    buttons = [
            [InlineKeyboardButton(text="📸 Получить file_id", callback_data="admin:get_file_id")],
        [
            InlineKeyboardButton(text="👁️ Посмотреть рубашки", callback_data="admin:view_card_back"),
            InlineKeyboardButton(text="🃏 Добавить рубашку", callback_data="admin:save_card_back")
        ],
        [
            InlineKeyboardButton(text="📜 Ошибки", callback_data="admin:errors"),
            InlineKeyboardButton(text="📦 Сделать бэкап", callback_data="admin:backup")
        ],
            [InlineKeyboardButton(text="🚪 Выйти.", callback_data="admin:exit")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для отмены действия"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:cancel")]
        ])

def get_delete_back_keyboard(back_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой удаления для рубашки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f"admin:del_back:{back_id}")]
        ])