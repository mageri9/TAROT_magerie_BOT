import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from services.ai_service import ask_oracle


class MockRedisClient:
    """Мок Redis для тестов Circuit Breaker"""

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


@pytest.fixture
def mock_redis():
    return MockRedisClient()


@pytest.fixture
def mock_openai_success():
    """Мок успешного ответа от OpenAI"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "✨ Тестовое предсказание ✨"
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150
    return mock_response


# ========== ТЕСТЫ ==========

@pytest.mark.asyncio
async def test_primary_model_success(mock_redis, mock_openai_success):
    """Тест 1: Основная модель отвечает успешно"""
    mock_create = AsyncMock(return_value=mock_openai_success)

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Маг",
            is_reversed=False,
            context="Хочу новую работу",
            db_meaning="Маг символизирует мастерство и волю.",
            redis_client=mock_redis,
        )

        assert result == "✨ Тестовое предсказание ✨"
        mock_create.assert_awaited_once()
        call_args = mock_create.call_args[1]
        assert call_args['model'] == "gemma-4-26b-a4b-it"


@pytest.mark.asyncio
async def test_fallback_on_timeout(mock_redis, mock_openai_success):
    """Тест 2: Таймаут основной → переключение на fallback"""
    mock_create = AsyncMock()
    mock_create.side_effect = [
        asyncio.TimeoutError(),
        mock_openai_success,
    ]

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Башня",
            is_reversed=True,
            context="Боюсь перемен",
            db_meaning="Башня — разрушение старого",
            redis_client=mock_redis
        )

        assert result == "✨ Тестовое предсказание ✨"
        assert mock_create.await_count == 2

        calls = [c[1]['model'] for c in mock_create.call_args_list]
        assert calls[0] == "gemma-4-26b-a4b-it"
        assert calls[1] == "gemma-4-31b-it"

        assert mock_redis.failures.get("gemma-4-26b-a4b-it") == 1


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold(mock_redis, mock_openai_success):
    """Тест 3: Circuit breaker размыкается после 3 ошибок"""
    mock_create = AsyncMock()
    mock_create.side_effect = [
        asyncio.TimeoutError(),
        asyncio.TimeoutError(),
        asyncio.TimeoutError(),
        mock_openai_success,
    ]

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        for i in range(3):
            await ask_oracle(
                card_name="Луна",
                is_reversed=False,
                context=f"Тест {i}",
                db_meaning="Луна — иллюзии",
                redis_client=mock_redis
            )

        # После 3 ошибок circuit должен быть открыт
        assert mock_redis.circuits.get("gemma-4-26b-a4b-it") == True

        # Следующий запрос должен сразу пойти в fallback
        await ask_oracle(
            card_name="Солнце",
            is_reversed=False,
            context="Тест после открытия",
            db_meaning="Солнце — радость",
            redis_client=mock_redis
        )

        calls = [c[1]['model'] for c in mock_create.call_args_list]
        # В последних запросах не должно быть основной модели
        assert "gemma-4-26b-a4b-it" not in calls[-1:]


@pytest.mark.asyncio
async def test_all_models_failed(mock_redis):
    """Тест 4: Все модели упали → заглушка"""
    mock_create = AsyncMock()
    mock_create.side_effect = Exception("API полностью лёг")

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Звезда",
            is_reversed=False,
            context="Нужна надежда",
            db_meaning="Звезда — надежда",
            redis_client=mock_redis
        )

        assert "Оракул сегодня немногословен" in result
        assert mock_create.await_count == 2


@pytest.mark.asyncio
async def test_auth_error_breaks_chain(mock_redis):
    """Тест 5: Ошибка 401 не пробует fallback"""
    mock_create = AsyncMock()
    mock_create.side_effect = Exception("401 Unauthorized")

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Смерть",
            is_reversed=False,
            context="Страх",
            db_meaning="Смерть — трансформация",
            redis_client=mock_redis
        )
        assert "Оракул сегодня немногословен" in result
        assert mock_create.await_count == 1


@pytest.mark.asyncio
async def test_circuit_breaker_skips_disabled_models(mock_redis):
    """Тест 6: Отключённые модели пропускаются"""
    mock_redis.circuits["gemma-4-26b-a4b-it"] = True

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Ответ fallback"

    mock_create = AsyncMock(return_value=mock_response)

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        await ask_oracle(
            card_name="Мир",
            is_reversed=False,
            context="",
            db_meaning="Мир — завершение",
            redis_client=mock_redis
        )

        call_args = mock_create.call_args[1]
        assert call_args['model'] == "gemma-4-31b-it"
        mock_create.assert_awaited_once()


@pytest.mark.asyncio
async def test_both_models_disabled(mock_redis):
    """Тест 7: Все модели отключены → сразу заглушка"""
    mock_redis.circuits["gemma-4-26b-a4b-it"] = True
    mock_redis.circuits["gemma-4-31b-it"] = True

    mock_create = AsyncMock()

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Влюблённые",
            is_reversed=False,
            context="",
            db_meaning="Влюблённые — выбор",
            redis_client=mock_redis
        )

        assert "Звёзды просят немного терпения" in result
        mock_create.assert_not_awaited()


@pytest.mark.asyncio
async def test_success_resets_circuit(mock_redis, mock_openai_success):
    """Тест 8: Успешный ответ сбрасывает счётчик ошибок"""
    mock_redis.failures["gemma-4-26b-a4b-it"] = 2

    mock_create = AsyncMock(return_value=mock_openai_success)

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        await ask_oracle(
            card_name="Колесница",
            is_reversed=False,
            context="",
            db_meaning="Колесница — движение",
            redis_client=mock_redis
        )

        assert mock_redis.failures.get("gemma-4-26b-a4b-it", 0) == 0
        assert mock_redis.circuits.get("gemma-4-26b-a4b-it", False) == False