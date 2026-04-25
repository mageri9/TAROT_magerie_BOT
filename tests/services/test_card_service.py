import pytest

from src.crud.card_back import add_card_back
from src.crud.tarot import save_tarot_card
from src.services.card import give_daily_card


@pytest.mark.asyncio
async def test_give_daily_card_success(test_db):
    """Успешное получение карты дня"""
    # Подготовка: карта в колоде рубашка есть
    await save_tarot_card(0, "Test Card", "Major", "Major", "0", "test_file_id")
    await add_card_back("test_card_back_id")

    card_id, back = await give_daily_card(123)

    assert card_id == 0
    assert back == "test_card_back_id"


@pytest.mark.asyncio
async def test_give_daily_card_already_today(test_db):
    """Уже получал сегодня"""
    await save_tarot_card(0, "Test Card", "Major", "Major", "0", "test_file_id")
    await add_card_back("test_card_back_id")

    # Первый раз
    await give_daily_card(123)

    # Второй раз
    card_id, back = await give_daily_card(123)

    assert card_id is None
    assert back is None


@pytest.mark.asyncio
async def test_give_daily_card_no_cards(test_db):
    """Нет карт в колоде"""
    await add_card_back("test_back_id")

    card_id, back = await give_daily_card(123)

    assert card_id is None
    assert back is None


@pytest.mark.asyncio
async def test_give_daily_card_no_backs(test_db):
    """Нет рубашек"""
    await save_tarot_card(0, "Test Card", "Major", "Major", "0", "test_file_id")

    card_id, back = await give_daily_card(123)

    assert card_id == 0
    assert back is None
