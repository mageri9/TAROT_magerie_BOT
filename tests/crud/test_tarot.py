import pytest
from src.crud.tarot import get_random_card, get_card_by_id, get_total_cards_count

@pytest.mark.asyncio
async def test_get_random_card(test_db):
    """Получение случайной карты"""
    #Добавим тестовую карту
    from src.crud.tarot import save_tarot_card
    await save_tarot_card(0, "Test Card", "Major", "Major", "0", "test_file_id")

    card = await get_random_card()
    assert card is not None
    assert card[0] == 0
    assert card[1] == "Test Card"

@pytest.mark.asyncio
async def test_get_card_by_id_not_found(test_db):
    """Получение несуществующей карты"""
    card = await get_card_by_id(999)
    assert card is None

@pytest.mark.asyncio
async def test_get_total_cards_count_empty(test_db):
    """Пустая колода"""
    count = await get_total_cards_count()
    assert count == 0