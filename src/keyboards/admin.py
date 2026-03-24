from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_keyboard():
    buttons = [
        [KeyboardButton(text="📸 Получить file_id")],
        [KeyboardButton(text="🃏 Сохранить рубашку")],
        [KeyboardButton(text="👁️ Посмотреть рубашку")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)