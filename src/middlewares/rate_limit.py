import time
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.dispatcher.event.bases import UNHANDLED
from loguru import logger

from core.redis import get_redis
from keyboards.user import card_of_the_day


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для защиты от спама и флуда.

    Использует Redis для хранения счётчиков, что позволяет:
    - Сохранять блокировки при перезапуске бота
    - Работать с несколькими инстансами бота одновременно

    Два уровня защиты:
    1. Короткая — спам кнопками/командами
       - Интервал: 1 сек
       - Лимит: 3 нарушения
       - Блокировка: 30 сек

    2. Длинная — поток сообщений
       - Лимит: 10 сообщений в минуту
       - Блокировка: 5 минут

    При блокировке:
    - Сообщение пользователя удаляется
    - Отправляется уведомление о блокировке
    - Все последующие действия игнорируются до истечения срока

    После любой обработки (кроме команд меню) автоматически
    восстанавливается основная клавиатура с кнопками:
    🔮 КАРТА ДНЯ | 📜 ПРОФИЛЬ | ❓ ПОМОЩЬ
    """
    def __init__(
            self,
            short_interval: float = 1.0,
            short_max_violations: int = 3,
            short_block: int = 30,
            long_limit: int = 10,
            long_window: int = 60,
            long_block: int = 300
    ):
        super().__init__()
        self.short_interval = short_interval
        self.short_max_violations = short_max_violations
        self.short_block = short_block
        self.long_limit = long_limit
        self.long_window = long_window
        self.long_block = long_block

    async def __call__(
            self,
            handler: Callable,
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        redis_client = get_redis()
        if not redis_client:
            return await handler(event, data)

        user_id = self._get_user_id(event)
        if not user_id:
            return await handler(event, data)

        now = time.time()

        # === 1. Короткая блокировка (спам кнопками/командами) ===
        last_key = f"rate:last:{user_id}"
        violations_key = f"rate:short_violations:{user_id}"
        block_key = f"rate:blocked:{user_id}"

        if await redis_client.exists(block_key):
            await self._cleanup(event)
            return UNHANDLED

        last = await redis_client.get(last_key)
        if last:
            last = float(last)
            if now - last < self.short_interval:
                violations = await redis_client.increment(violations_key)
                await redis_client.expire(violations_key, self.short_block * 2)

                if violations >= self.short_max_violations:
                    await redis_client.set(block_key, "1", ttl=self.short_block)
                    logger.warning(f"User {user_id} short-blocked for {self.short_block}s")
                    await self._notify_user(event, f"⛔ Блокировка {self.short_block} сек (спам)")
                    await self._cleanup(event)
                    return UNHANDLED
            else:
                await redis_client.delete(violations_key)

        await redis_client.set(last_key, str(now), ttl=max(1, int(self.short_interval * 2)))

        # === 2. Длинная блокировка (поток сообщений) ===
        timestamps_key = f"rate:timestamps:{user_id}"
        long_block_key = f"rate:long_blocked:{user_id}"

        if await redis_client.exists(long_block_key):
            await self._cleanup(event)
            return UNHANDLED

        await redis_client.lpush(timestamps_key, str(now))
        await redis_client.expire(timestamps_key, self.long_window * 2)

        all_timestamps = await redis_client.lrange(timestamps_key, 0, -1)
        recent = [float(t) for t in all_timestamps if now - float(t) < self.long_window]

        if len(recent) >= self.long_limit:
            await redis_client.set(long_block_key, "1", ttl=self.long_block)
            logger.warning(f"User {user_id} long-blocked for {self.long_block}s")
            await self._notify_user(event, f"⛔ Блокировка {self.long_block} сек (слишком много сообщений)")
            await self._cleanup(event)
            return UNHANDLED

        # === 3. Нормальный проход ===
        result = await handler(event, data)

        return result

    @staticmethod
    def _get_user_id(event: Update) -> int | None:
        if event.message:
            return event.message.from_user.id
        elif event.callback_query:
            return event.callback_query.from_user.id
        return None

    @staticmethod
    async def _cleanup(event: Update):
        if event.message:
            try:
                await event.message.delete()
            except Exception:
                pass

    @staticmethod
    async def _notify_user(event: Update, text: str):
        if event.message:
            await event.message.answer(text)
        elif event.callback_query:
            await event.callback_query.answer(text, show_alert=True)

