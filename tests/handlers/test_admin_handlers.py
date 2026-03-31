import pytest
from datetime import datetime

from aiogram import types
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendMessage
from aiogram.types import Update, Message, Chat, User, CallbackQuery




def make_message(user_id: int, text: str, message: Message = None):
    return Message(
        message_id=1,
        chat=Chat(id=user_id, type=ChatType.PRIVATE),
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        date=datetime.now(),
        text=text,
        message = message
    )

def make_photo_message(user_id: int, file_id: str) -> Message:
    """Сообщение с фото"""
    return Message(
        message_id=2,
        chat=Chat(id=user_id, type=ChatType.PRIVATE),
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        date=datetime.now(),
        photo=[types.PhotoSize(file_id=file_id, file_unique_id=file_id, width=100, height=100)],
    )

def make_callback(user_id: int, data: str, message: Message = None) -> CallbackQuery:
    return CallbackQuery(
        id="111",
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        chat_instance="test",
        data=data,
        message=message
    )

@pytest.mark.asyncio
async def test_admin_command(dp, bot, test_db, monkeypatch):
    """Тест /admin для админа"""
    from src.core.config import settings
    settings.ADMIN_IDS = [123]

    bot.add_result_for(SendMessage, ok=True)

    update = Update(update_id=1, message=make_message(123, "/admin"))
    result = await dp.feed_update(bot, update)
    assert result is not UNHANDLED

    outgoing = bot.get_request()
    assert isinstance(outgoing, SendMessage)
    assert "admin menu" in outgoing.text.lower()



@pytest.mark.asyncio
async def test_admin_commands_not_admin(dp, bot, test_db, monkeypatch):
    """Тест /admin для не-админа"""
    from src.core.config import settings
    settings.ADMIN_IDS = [999]

    bot.add_result_for(SendMessage, ok=True)

    update = Update(update_id=1, message=make_message(123, "/admin"))
    result = await dp.feed_update(bot, update)
    assert result is UNHANDLED



