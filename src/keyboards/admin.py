from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    buttons = [
        [
            InlineKeyboardButton(text="📸 Получить file_id", callback_data="admin:get_file_id"),
            InlineKeyboardButton(text="🃏 Сохранить рубашку", callback_data="admin:save_card_back")
        ],
        [
            InlineKeyboardButton(text="👁️ Посмотреть рубашку", callback_data="admin:view_card_back")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin:cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для отмены действия"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:cancel")]
            ]
    )
