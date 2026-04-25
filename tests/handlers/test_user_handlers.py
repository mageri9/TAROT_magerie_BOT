from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendMessage, SendPhoto
from aiogram.types import Chat, Message, Update, User

from src.crud.card_back import add_card_back
from src.crud.tarot import save_tarot_card


def make_message(user_id: int, text: str) -> Message:
    """Создает фейковое сообщение"""
    return Message(
        message_id=1,
        chat=Chat(id=user_id, type=ChatType.PRIVATE),
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        date=datetime.now(),
        text=text,
    )


@pytest.mark.asyncio
async def test_start_handler(dp, bot, test_db):
    """Тест команды /start"""
    bot.add_result_for(SendMessage, ok=True)

    user_id = 123456
    update = Update(update_id=1, message=make_message(user_id, "/start"))

    result = await dp.feed_update(bot, update)
    assert result is not UNHANDLED

    outgoing = bot.get_request()
    assert isinstance(outgoing, SendMessage)
    assert "добро пожаловать" in outgoing.text.lower()


@pytest.mark.asyncio
async def test_card_of_day_success(dp, bot, test_db, monkeypatch):
    """Тест кнопки 'КАРТА ДНЯ' - успешное получение"""
    await save_tarot_card(0, "Test Card", "Major", "Major", "0", "test_file_id")
    await add_card_back("test_card_back_id")

    bot.add_result_for(SendPhoto, ok=True)

    user_id = 123456
    update = Update(update_id=1, message=make_message(user_id, "🔮 КАРТА ДНЯ 🔮"))

    result = await dp.feed_update(bot, update)
    assert result is not UNHANDLED

    outgoing = bot.get_request()
    assert isinstance(outgoing, SendPhoto)

    assert outgoing.photo == "test_card_back_id"
    assert "Пока не открыли карту" in outgoing.caption


@pytest.mark.asyncio
async def test_card_of_day_already_today(dp, bot, test_db, monkeypatch):
    """Тест кнопки 'КАРТА ДНЯ' - уже получал сегодня"""

    async def mock_give_daily_card(user_id):
        return (None, None)

    monkeypatch.setattr("src.services.card.give_daily_card", mock_give_daily_card)

    bot.add_result_for(SendMessage, ok=True)

    user_id = 123456
    update = Update(update_id=1, message=make_message(user_id, "🔮 КАРТА ДНЯ 🔮"))

    result = await dp.feed_update(bot, update)
    assert result is not UNHANDLED

    outgoing = bot.get_request()
    assert isinstance(outgoing, SendMessage)
    assert "уже получали" in outgoing.text
