import pytest
import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.core.db import db
from src.database.init import init_all_tables
from src.core.router_manager import setup_routers
from tests.mocked_aiogram import MockedBot, MockedSession


@pytest.fixture
async def test_db():
    """Временная БД в памяти для тестов"""
    old_url = db.db_url
    db.db_url = ":memory:"
    await db.connect()
    await init_all_tables()
    yield db
    await db.close()
    db.db_url = old_url

@pytest.fixture
def bot():
    """Мок-бот для тестирования хэндлеров"""
    bot = MockedBot()
    bot.session = MockedSession()
    return bot

@pytest.fixture
def dp(bot, test_db):
    """Диспетчер с роутерами и тестовой БД"""
    dp = Dispatcher(storage=MemoryStorage())
    router = setup_routers()
    for r in [router] + router.sub_routers:
        r._parent_router = None
    dp.include_router(router)
    return dp

@pytest.fixture
def event_loop():
    """Фикстура для asyncio"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()