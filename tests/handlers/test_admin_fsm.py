import pytest
from aiogram.fsm.context import FSMContext



from test_admin_handlers import make_callback, make_photo_message, make_message
from aiogram.methods import SendMessage, AnswerCallbackQuery
from aiogram.types import Update

from src.handlers.admin.callback import AdminStates


@pytest.mark.asyncio
async def test_admin_save_card_back_start(dp, bot, test_db, monkeypatch):
    """Тест начала сохранения рубашки — переход в состояние waiting_for_save_back"""
    from src.core.config import settings
    settings.ADMIN_IDS = [123]

    # Мокаем ответы Telegram
    bot.add_result_for(AnswerCallbackQuery, ok=True, result=None)
    bot.add_result_for(SendMessage, ok=True, result=None)

    # Отправляем callback от админа
    message = make_message(123, "test")
    callback = make_callback(123, "admin:save_card_back", message=message)

    await dp.feed_update(bot, Update(update_id=1, callback_query=callback))

    # Получаем FSM-контекст
    fsm_context: FSMContext = dp.fsm.get_context(bot, user_id=123, chat_id=123)
    state = await fsm_context.get_state()
    print(f"Состояние FSM: {state}")
    assert state == AdminStates.waiting_for_save_back


@pytest.mark.asyncio
async def test_admin_handle_photo_for_save_back(dp, bot, test_db, monkeypatch):
    """Тест сохранения рубашки — отправка фото"""
    from src.core.config import settings
    settings.ADMIN_IDS = [123]


    # Устанавливаем состояние вручную
    fsm_context: FSMContext = dp.fsm.get_context(bot, user_id=123, chat_id=123)
    await fsm_context.set_state(AdminStates.waiting_for_save_back)

    bot.add_result_for(SendMessage, ok=True)

    # Отправляем фото
    photo_message = make_photo_message(123, "test_photo_id")
    await dp.feed_update(bot, Update(update_id=1, message=photo_message))

    # Проверяем, что рубашка сохранилась в БД
    backs = await test_db.fetchall("SELECT file_id FROM card_back")
    assert len(backs) == 1
    assert backs[0][0] == "test_photo_id"

    # Проверяем, что состояние сбросилось
    state = await fsm_context.get_state()
    assert state is None