from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from core.config import settings


class IsAdmin(BaseFilter):
     async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in settings.ADMIN_IDS

