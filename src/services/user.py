from aiogram.types import User

from ..crud import get_user, create_user, update_username


async def register_user(user_id: int, username: str = None):
    """Зарегистрировать пользователя, если его нет"""
    user = await get_user(user_id)
    if not user:
        await create_user(user_id, username)
        return True
    return False

async def get_or_create_user(user_id: int, username: str = None):
    """Получить пользователя или создать"""
    user = await get_user(user_id)
    if not user:
        await create_user(user_id, username)
        user = await get_user(user_id)
        return user
