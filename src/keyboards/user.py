from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def card_of_the_day():
    card = [
                [
                KeyboardButton(text='🔮 КАРТА ДНЯ 🔮')
                ]
            ]
    return ReplyKeyboardMarkup(keyboard=card, resize_keyboard=True)


def reroll_and_share():
    pass

def open_card_button() -> InlineKeyboardMarkup:
    open_button = [
        [InlineKeyboardButton(text="Открыть",  callback_data="open_card")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=open_button)

