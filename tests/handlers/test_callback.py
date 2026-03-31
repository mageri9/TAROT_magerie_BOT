import pytest

from aiogram.dispatcher.event.bases import UNHANDLED

from aiogram.methods import EditMessageMedia, AnswerCallbackQuery
from aiogram.types import Update, CallbackQuery, User, Message

from src.crud.tarot import save_tarot_card
from tests.conftest import test_db
from tests.handlers.test_user_handlers import make_message


def make_callback(user_id: int, data: str, message: Message = None) -> CallbackQuery:
    """Создает файловый callback"""
    return CallbackQuery(
        id="111",
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        chat_instance="test",
        data=data,
        message=message
    )

@pytest.mark.asyncio
async def test_open_card(dp, bot, test_db):
    """Тест открытия карты"""
    await save_tarot_card(
        card_id=0,
        name="Шут",
        arcana="Major",
        suit="Major",
        card_number="0",
        file_id="card_file_id",
    )
    await test_db.execute(
        "UPDATE tarot_cards SET meaning_direct = 'Начало пути', meaning_reversed = 'Глупость' WHERE id = 0"
    )
    bot.add_result_for(EditMessageMedia, ok=True)
    bot.add_result_for(AnswerCallbackQuery, ok=True)

    user_id = 123
    message = make_message(123, "test")
    callback = make_callback(user_id, "open_card:0", message=message)
    update = Update(update_id=1, callback_query=callback)

    result = await dp.feed_update(bot, update)
    assert result is not UNHANDLED

    outgoing = bot.get_request()
    assert isinstance(outgoing, EditMessageMedia)

@pytest.mark.asyncio
async def test_reroll_card(dp, bot, test_db):
    """Тест реролла карты"""
    await save_tarot_card(0, "Шут", "Major", "Major", "0", "file_0")
    await save_tarot_card(1, "Маг", "Major", "Major", "1", "file_1")

    bot.add_result_for(EditMessageMedia, ok=True)
    bot.add_result_for(AnswerCallbackQuery, ok=True)

    user_id = 123
    message = make_message(123, "some text")
    callback = make_callback(user_id, "reroll:0", message=message)
    update = Update(update_id=1, callback_query=callback)

    result = await dp.feed_update(bot, update)
    assert result is not UNHANDLED

    outgoing = bot.get_request()
    assert isinstance(outgoing, EditMessageMedia)

@pytest.mark.parametrize("is_reversed", [True, False])
@pytest.mark.asyncio
async def test_open_card_position(dp, bot, test_db, monkeypatch, is_reversed):
    """Параметризованный тест: прямая/перевёрнутая карта"""
    def fixed_random_choice(seq):
        return is_reversed

    monkeypatch.setattr("random.choice", fixed_random_choice)

    await save_tarot_card(0, "Шут", "Major", "Major", "0", "file_0")
    await test_db.execute(
        "UPDATE tarot_cards SET meaning_direct = 'Прямое', meaning_reversed = 'Перевёрнутое' WHERE id = 0"
    )

    bot.add_result_for(EditMessageMedia, ok=True)
    bot.add_result_for(AnswerCallbackQuery, ok=True)

    message = make_message(123, "some text")
    callback = make_callback(123, "open_card:0", message=message)
    await dp.feed_update(bot, Update(update_id=1, callback_query=callback))

    outgoing = bot.get_request()
    assert isinstance(outgoing, EditMessageMedia)

    if is_reversed:
        assert "перевёрнутая" in outgoing.media.caption
    else:
        assert "перевёрнутая" not in outgoing.media.caption



