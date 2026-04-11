import time
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Update
from aiogram.dispatcher.event.bases import UNHANDLED
from loguru import logger
from src.keyboards.user import card_of_the_day


class RateLimitMiddleware(BaseMiddleware):
    def __init__(
            self,
            short_interval: float = 1.0,  # 1 секунда между действиями
            short_max_violations: int = 3,  # 3 нарушения
            short_block: int = 30,  # блок на 30 секунд
            long_limit: int = 10,  # 10 сообщений
            long_window: int = 60,  # в минуту
            long_block: int = 300  # блок на 5 минут
    ):
        super().__init__()
        # Короткая блокировка (спам кнопками)
        self.short_interval = short_interval
        self.short_max_violations = short_max_violations
        self.short_block = short_block

        # Длинная блокировка (поток сообщений)
        self.long_limit = long_limit
        self.long_window = long_window
        self.long_block = long_block

        # Хранилища
        self.last_requests = {}  # для короткой блокировки
        self.violations = {}  # для короткой блокировки
        self.request_timestamps = {}  # для длинной блокировки
        self.blocked_until = {}  # общая блокировка

    async def __call__(
            self,
            handler: Callable,
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        user_id = self._get_user_id(event)
        if not user_id:
            return await handler(event, data)

        now = time.time()

        # === 1. Общая проверка блокировки ===
        if user_id in self.blocked_until and now < self.blocked_until[user_id]:
            await self._cleanup(event)
            return UNHANDLED

        # === 2. Короткая блокировка (спам кнопками/командами) ===
        last = self.last_requests.get(user_id, 0)
        if now - last < self.short_interval:
            self.violations[user_id] = self.violations.get(user_id, 0) + 1
            violations = self.violations[user_id]

            if violations >= self.short_max_violations:
                self.blocked_until[user_id] = now + self.short_block
                logger.warning(f"User {user_id} short-blocked for {self.short_block}s")
                await self._notify_user(event, f"⛔ Блокировка {self.short_block} сек (спам)")

            await self._cleanup(event)
            return UNHANDLED

        # === 3. Длинная блокировка (поток сообщений) ===
        if user_id not in self.request_timestamps:
            self.request_timestamps[user_id] = []

        # Очищаем старые метки
        self.request_timestamps[user_id] = [
            t for t in self.request_timestamps[user_id] if now - t < self.long_window
        ]

        if len(self.request_timestamps[user_id]) >= self.long_limit:
            self.blocked_until[user_id] = now + self.long_block
            logger.warning(f"User {user_id} long-blocked for {self.long_block}s")
            await self._notify_user(event, f"⛔ Блокировка {self.long_block} сек (слишком много сообщений)")
            await self._cleanup(event)
            return UNHANDLED

        # === 4. Нормальный проход ===
        self.violations[user_id] = 0
        self.last_requests[user_id] = now
        self.request_timestamps[user_id].append(now)

        result = await handler(event, data)

        # === 5. Восстановление клавиатуры (тихо) ===
        await self._restore_keyboard(event)

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
        """Удаляет сообщение пользователя"""
        if event.message:
            try:
                await event.message.delete()
            except Exception:
                pass

    @staticmethod
    async def _notify_user(event: Update, text: str):
        """Отправляет уведомление о блокировке"""
        if event.message:
            await event.message.answer(text)
        elif event.callback_query:
            await event.callback_query.answer(text, show_alert=True)

    @staticmethod
    async def _restore_keyboard(event: Update):
        """Тихо восстанавливает клавиатуру через сообщение"""
        if not event.message:
            return

        text = event.message.text
        if text and text not in ["/start", "/menu", "🔮 КАРТА ДНЯ 🔮", "📜 ПРОФИЛЬ 📜"]:
            try:
                await event.message.answer(
                    "🔮",
                    reply_markup=card_of_the_day(),
                    disable_notification=True
                )
            except Exception:
                pass