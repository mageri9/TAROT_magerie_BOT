import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.dispatcher.event.bases import UNHANDLED
from loguru import logger


class MinuteLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 10, block_minutes: int = 5):
        self.limit = limit
        self.block_seconds = block_minutes * 60
        self.requests = {}
        self.blocked_until = {}

    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        # Получаем user_id из Update
        user_id = None
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        else:
            return await handler(event, data)

        now = time.time()

        # Проверка блокировки
        if user_id in self.blocked_until and now < self.blocked_until[user_id]:
            if event.message:
                try:
                    await event.message.delete()
                except Exception:
                    pass
            return UNHANDLED


        # Очистка старых меток
        if user_id in self.requests:
            self.requests[user_id] = [t for t in self.requests[user_id] if now - t < 60]
        else:
            self.requests[user_id] = []

        # Проверка лимита
        if len(self.requests[user_id]) >= self.limit:
            self.blocked_until[user_id] = now + self.block_seconds
            logger.warning(f"User {user_id} minute-limit blocked for {self.block_seconds}s")
            await self._notify_user(event, user_id)
            return UNHANDLED

        # Всё хорошо
        self.requests[user_id].append(now)
        return await handler(event, data)

    async def _notify_user(self, event: Update, user_id: int):
        """Отправляет уведомление пользователю о блокировке"""
        if event.message:
            await event.message.answer("🚫 Слишком много сообщений! Блокировка на 5 минут.")
        elif event.callback_query:
            await event.callback_query.answer("🚫 Блокировка на 5 минут", show_alert=True)