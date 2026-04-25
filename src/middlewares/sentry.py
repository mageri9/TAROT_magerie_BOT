from typing import Any, Awaitable, Callable, Dict

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class SentryMiddleware(BaseMiddleware):
    """Отправляет необработанные ошибки в Sentry и пробрасывает дальше."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            sentry_sdk.set_user(
                {"id": user.id, "username": user.username, "full_name": user.full_name}
            )

        try:
            return await handler(event, data)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise
