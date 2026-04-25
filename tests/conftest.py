import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
from unittest.mock import MagicMock

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from mocked_aiogram import MockedBot, MockedSession

from src.core.db import db
from src.core.router_manager import setup_routers
from src.database.init import init_all_tables


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


class MockRedisClient:
    """Мок Redis для тестов"""

    def __init__(self):
        self.data = {}
        self.failures = {}
        self.circuits = {}

    async def is_circuit_open(self, model: str) -> bool:
        return self.circuits.get(model, False)

    async def record_failure(self, model: str) -> int:
        self.failures[model] = self.failures.get(model, 0) + 1
        return self.failures[model]

    async def open_circuit(self, model: str) -> None:
        self.circuits[model] = True

    async def reset_circuit(self, model: str) -> None:
        self.failures[model] = 0
        self.circuits[model] = False

    # Методы кэша
    def _get_oracle_cache_key(self, card_name: str, is_reversed: bool, context: str) -> str:
        import hashlib

        normalized = " ".join(context.lower().split()) if context else ""
        raw = f"{card_name}:{is_reversed}:{normalized}"
        hash_val = hashlib.md5(raw.encode()).hexdigest()[:12]
        return f"oracle:cache:{hash_val}"

    async def cache_oracle_response(
        self, card_name: str, is_reversed: bool, context: str, response: str, ttl: int = None
    ) -> None:
        key = self._get_oracle_cache_key(card_name, is_reversed, context)
        self.data[key] = response

    async def get_cached_oracle_response(
        self, card_name: str, is_reversed: bool, context: str
    ) -> str | None:
        key = self._get_oracle_cache_key(card_name, is_reversed, context)
        return self.data.get(key)

    async def get(self, key: str) -> str | None:
        return self.data.get(key)

    async def set(self, key: str, value: str, ttl: int = None) -> None:
        self.data[key] = value


@pytest.fixture
def mock_redis():
    return MockRedisClient()


@pytest.fixture
def mock_openai_success():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "✨ Тестовое предсказание ✨"
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150
    return mock_response
