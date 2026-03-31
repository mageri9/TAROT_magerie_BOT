import pytest
from src.crud.card_back import add_card_back, get_random_card_back, get_all_card_backs, delete_card_back

@pytest.mark.asyncio
async def test_add_card_back(test_db):
    """Добавление рубашки"""
    file_id = "test_file_id_123"
    await add_card_back(file_id)

    backs = await get_all_card_backs()
    assert len(backs) == 1
    assert backs[0][1] == file_id

@pytest.mark.asyncio
async def test_get_random_card_back(test_db):
    """Получение случайной рубашки"""
    await add_card_back("file_1")
    await add_card_back("file_2")

    result = await get_random_card_back()
    assert result in ["file_1", "file_2"]

@pytest.mark.asyncio
async def test_delete_card_back(test_db):
    """Удаление рубашки"""
    await add_card_back("file_1")
    backs = await get_all_card_backs()
    back_id = backs[0][0]

    await delete_card_back(back_id)

    backs = await get_all_card_backs()
    assert len(backs) == 0