from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from typing import Optional
import json
import time

class RedisClient:
    """
        Обёртка над Redis для удобной работы.
        Предоставляет:
        - storage для FSM (aiogram)
        - методы для кэша
        - методы для AI-памяти
        - методы для блокировок
    """

    def __init__(self, url: str = 'redis://localhost:6379/0'):
        self._redis = Redis.from_url(url, decode_responses=True)
        self.storage = RedisStorage(
            redis=self._redis,
            key_builder=DefaultKeyBuilder(prefix='tarot_fsm', separator=":")
        )

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Сохранить строку по ключу."""
        await self._redis.set(key, value, ex=ttl)

    async def get(self, key: str) -> Optional[str]:
        """Получить строку по ключу."""
        return await self._redis.get(key)

    async def delete(self, key: str) -> None:
        """Удалить ключ."""
        await self._redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Проверить, существует ли ключ."""
        return await self._redis.exists(key) > 0


    async def set_json(self, key: str, data: dict, ttl: Optional[int] = None) -> None:
        """Сохранить словарь как JSON-строку."""
        await self._redis.set(key, json.dumps(data, ensure_ascii=False), ex=ttl)

    async def get_json(self, key: str) -> Optional[dict]:
        """Получить словарь из JSON-строки."""
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def cache_card(self, card_id: int, card_data: dict, ttl: int = 3600) -> None:
        """Закэшировать данные карты."""
        await self.set_json(f"card:{card_id}", card_data, ttl)

    async def get_cached_card(self, card_id: int) -> Optional[dict]:
        """Получить карту из кэша."""
        return await self.get_json(f"card:{card_id}")

    async def invalidate_card_cache(self, card_id: int) -> None:
        """Сбросить кэш карты."""
        await self.delete(f"card:{card_id}")


    async def add_chat_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю диалога с AI.
            Используется для команды /chat."""
        key = f"chat_history:{user_id}"

        msg = json.dumps({
            "role": role,
            "content": content,
            "timestamp": time.time()
        }, ensure_ascii=False)

        await self._redis.lpush(key, msg)

        await self._redis.ltrim(key, 0, 19)

        await self._redis.expire(key, 3600)

    async def get_chat_history(self, user_id: int, limit: int = 10) -> list[dict]:
        """Получить историю диалога для AI."""
        key = f"chat_history:{user_id}"

        raw = await self._redis.lrange(key, 0, limit - 1)
        return [json.loads(m) for m in reversed(raw)]

    async def clear_chat_history(self, user_id: int) -> None:
        """Очистить историю диалога."""
        await self._redis.delete(f"chat_history:{user_id}")


    async def increment_rate(self, user_id: int, window: int = 60) -> int:
        """Увеличить счётчик запросов пользователя. Используется для защиты от спама."""
        key = f"rate:user:{user_id}"

        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, window)
        return count

    async def get_rate_count(self, user_id: int) -> int:
        """Получить текущий счётчик запросов."""
        key = f"rate:user:{user_id}"

        count = await self._redis.get(key)
        return int(count) if count else 0


    async def acquire_lock(self, user_id: int, lock_name: str, ttl: int = 30) -> bool:
        """Захватить блокировку.
        Используется, чтобы пользователь не мог запустить два платных расклада одновременно."""
        key = f"lock:{user_id}:{lock_name}"

        result = await self._redis.set(key, 1, nx=True, ex=ttl)

        return result is not None

    async def release_lock(self, user_id: int, lock_name: str) -> None:
        """Освободить блокировку."""
        await self._redis.delete(f"lock:{user_id}:{lock_name}")


    async def ping(self) -> bool:
        """Проверить соединение Redis при старте бота."""
        try:
            return await self._redis.ping()
        except Exception:
            return False

    async def get_info(self) -> dict:
        """Получить информацию о сервере Redis."""
        info = await self._redis.info()
        return {
            "version": info.get("redis_version"),
            "used_memory": info.get("used_memory"),
            "connected_clients": info.get("connected_clients"),
            "uptime_days": info.get("uptime_days"),
        }

redis_client = None

def init_redis(url: str) -> RedisClient:
    global redis_client
    redis_client = RedisClient(url)
    return redis_client