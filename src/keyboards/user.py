from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def card_of_the_day():
    card = [
                [KeyboardButton(text='🔮 КАРТА ДНЯ 🔮')],
                [KeyboardButton(text='📜 ПРОФИЛЬ 📜')],
                [KeyboardButton(text='❓ ПОМОЩЬ ❓')]
           ]
    return ReplyKeyboardMarkup(keyboard=card, resize_keyboard=True)


def open_card_actions_keyboard(card_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками Реролл и Оракул"""
    buttons = [
        [InlineKeyboardButton(text="✨ Можешь посмотреть ещё одну. ✨", callback_data=f"reroll:{card_id}")],
        [InlineKeyboardButton(text="🔮 Толкование Оракула 🔮", callback_data=f"oracle:{card_id}")]
              ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def oracle_only_keyboard(card_id: int) -> InlineKeyboardMarkup:
    """Клавиатура только с Оракулом"""
    buttons = [
        [InlineKeyboardButton(text="🔮 Толкование Оракула 🔮", callback_data=f"oracle:{card_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def open_card_button(card_id: int = None) -> InlineKeyboardMarkup:
    """Кнопка открытия карты (для рубашки)"""
    if card_id is not None:
        callback_data = f"open_card:{card_id}"
    else:
        callback_data = "open_card"

    open_button = [
        [InlineKeyboardButton(text="🔮 Открыть", callback_data=callback_data)]
                  ]
    return InlineKeyboardMarkup(inline_keyboard=open_button)