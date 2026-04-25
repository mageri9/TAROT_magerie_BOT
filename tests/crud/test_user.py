import pytest

from src.crud.user import create_user, get_user, update_username


@pytest.mark.asyncio
async def test_create_user(test_db):
    """Создание нового пользователя"""
    user_id = 123456
    username = "testuser"

    await create_user(user_id, username)

    user = await get_user(user_id)
    assert user is not None
    assert user[1] == username


@pytest.mark.asyncio
async def test_get_user_not_found(test_db):
    """Получение несуществующего пользователя"""
    user = await get_user(999999)
    assert user is None


@pytest.mark.asyncio
async def test_update_username(test_db):
    """Обновление username"""
    user_id = 123456
    await create_user(user_id, "oldname")

    await update_username(user_id, "newname")

    user = await get_user(user_id)
    assert user[1] == "newname"
