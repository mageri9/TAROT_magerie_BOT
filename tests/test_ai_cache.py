import pytest
from unittest.mock import AsyncMock, patch
from services.ai_service import ask_oracle


@pytest.mark.asyncio
async def test_cache_hit_returns_cached_response(mock_redis, mock_openai_success):
    """Тест 1: Ответ берётся из кэша, AI не вызывается"""

    # Предварительно кладём ответ в кэш
    await mock_redis.cache_oracle_response("Маг", False, "Хочу работу", "✨ Предсказание из кэша ✨")

    mock_create = AsyncMock()

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Маг",
            is_reversed=False,
            context="Хочу работу",
            db_meaning="Маг — мастерство",
            redis_client=mock_redis
        )

    assert result == "✨ Предсказание из кэша ✨"
    mock_create.assert_not_awaited()  # AI не вызывался


@pytest.mark.asyncio
async def test_cache_miss_calls_ai_and_caches(mock_redis, mock_openai_success):
    """Тест 2: Промах кэша → вызов AI → сохранение в кэш"""

    mock_create = AsyncMock(return_value=mock_openai_success)

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Маг",
            is_reversed=False,
            context="Новый контекст",
            db_meaning="Маг — мастерство",
            redis_client=mock_redis
        )

    assert result == "✨ Тестовое предсказание ✨"
    mock_create.assert_awaited_once()

    # Проверяем, что ответ попал в кэш
    cached = await mock_redis.get_cached_oracle_response("Маг", False, "Новый контекст")
    assert cached == "✨ Тестовое предсказание ✨"


@pytest.mark.asyncio
async def test_cache_disabled_bypasses_cache(mock_redis, mock_openai_success):
    """Тест 3: Кэш отключен → всегда идём в AI"""

    # Кладём в кэш
    await mock_redis.cache_oracle_response("Маг", False, "Тест", "Из кэша")

    # Отключаем кэш в настройках
    with patch('services.ai_service.settings.AI_CACHE_ENABLED', False):
        mock_create = AsyncMock(return_value=mock_openai_success)

        with patch('services.ai_service.client.chat.completions.create', mock_create):
            result = await ask_oracle(
                card_name="Маг",
                is_reversed=False,
                context="Тест",
                db_meaning="Маг",
                redis_client=mock_redis
            )

    assert result == "✨ Тестовое предсказание ✨"
    mock_create.assert_awaited_once()  # AI вызван, несмотря на кэш


@pytest.mark.asyncio
async def test_failed_response_not_cached(mock_redis):
    """Тест 4: Ошибка AI → заглушка НЕ кэшируется"""

    mock_create = AsyncMock(side_effect=Exception("API упал"))

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        result = await ask_oracle(
            card_name="Маг",
            is_reversed=False,
            context="Тест",
            db_meaning="Маг",
            redis_client=mock_redis
        )

    assert "Оракул сегодня немногословен" in result

    # Проверяем, что заглушка НЕ попала в кэш
    cached = await mock_redis.get_cached_oracle_response("Маг", False, "Тест")
    assert cached is None


@pytest.mark.asyncio
async def test_different_contexts_have_different_cache_keys(mock_redis, mock_openai_success):
    """Тест 5: Разный контекст → разные ключи кэша"""

    mock_create = AsyncMock(return_value=mock_openai_success)

    with patch('services.ai_service.client.chat.completions.create', mock_create):
        # Первый запрос
        await ask_oracle("Маг", False, "Контекст 1", "Маг", mock_redis)
        # Второй запрос с другим контекстом
        await ask_oracle("Маг", False, "Контекст 2", "Маг", mock_redis)

    # AI вызван дважды (разные контексты)
    assert mock_create.await_count == 2

    # В кэше два разных ключа
    cached1 = await mock_redis.get_cached_oracle_response("Маг", False, "Контекст 1")
    cached2 = await mock_redis.get_cached_oracle_response("Маг", False, "Контекст 2")
    assert cached1 is not None
    assert cached2 is not None