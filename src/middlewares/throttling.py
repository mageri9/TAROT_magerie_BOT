import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.event.bases import UNHANDLED
from loguru import logger


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0, max_violations: int = 3, block_time: int = 30):
        super().__init__()
        self.rate_limit = rate_limit
        self.last_requests = {}
        self.max_violations = max_violations
        self.block_time = block_time

        self.last_requests = {}
        self.violations = {}
        self.blocked_until = {}

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()

        if user_id in self.blocked_until and now < self.blocked_until[user_id]:
            if isinstance(event, Message):
                await event.delete()
            return UNHANDLED

        last = self.last_requests.get(user_id, 0)

        if now - last < self.rate_limit:
            self.violations[user_id] = self.violations.get(user_id, 0) + 1
            violations = self.violations[user_id]

            if violations >= self.max_violations:
                logger.warning(f"User {user_id} blocked for {self.block_time}s")
                self.blocked_until[user_id] = now + self.block_time
                await event.answer("🚫 Блокировка 30 сек", show_alert=isinstance(event, CallbackQuery))

            return UNHANDLED

        self.violations[user_id] = 0
        self.last_requests[user_id] = now
        return await handler(event, data)

