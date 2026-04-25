from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Update
from loguru import logger


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramForbiddenError as e:
            user_id = self._get_user_id(event)
            logger.warning(f"⚠️ User {user_id} blocked bot or deleted chat: {e}")
            return
        except TelegramBadRequest as e:
            logger.warning(f"⚠️ Bad request: {e}")
            return
        except Exception as e:
            logger.error(f"❌ Unhandled error: {e}")
            return

    def _get_user_id(self, event: Update) -> str:
        """Извлекаем user_id из Update."""
        if event.message:
            return event.message.from_user.id
        elif event.callback_query:
            return event.callback_query.from_user.id
        return "unknown"
