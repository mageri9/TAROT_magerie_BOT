from datetime import date, timedelta

import pytest

from src.crud.card import can_get_card, save_card_requests


@pytest.mark.asyncio
async def test_can_get_card_first_time(test_db):
    """Первый раз - можно получить карту"""
    user_id = 123
    result = await can_get_card(user_id)
    assert result is True


@pytest.mark.asyncio
async def test_can_get_card_today(test_db):
    """Уже получал сегодня - нельзя"""
    user_id = 123
    await save_card_requests(user_id)

    result = await can_get_card(user_id)
    assert result is False


@pytest.mark.asyncio
async def test_can_get_card_yesterday(test_db):
    """Получал вчера - можно"""
    user_id = 123

    # Вручную меняем дату в БД
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    await test_db.execute(
        "INSERT INTO user_cards (user_id, last_card_date) VALUES (1$, 2$)", (user_id, yesterday)
    )

    result = await can_get_card(user_id)
    assert result is True
