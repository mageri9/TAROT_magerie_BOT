from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from ..core.config import settings


class IsAdmin(BaseFilter):
     async def __call__(self, obj: TelegramObject) -> bool:
        print(f"🔍 IsAdmin check: user_id={obj.from_user.id}, admin_ids={settings.ADMIN_IDS}")
        return obj.from_user.id in settings.ADMIN_IDS

