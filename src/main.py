import asyncio
import sys
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger

from core.config import Settings
from core.db import db
from core.logger import setup_logging
from core.redis import init_redis
from core.router_manager import setup_routers
from core.sentry_init import init_sentry
from filters.chat_type import ChatTypeFilter
from middlewares.error_handler import ErrorHandlerMiddleware
from middlewares.logger import LoggerMiddleware
from middlewares.rate_limit import RateLimitMiddleware
from middlewares.sentry import SentryMiddleware


async def main():
    setup_logging()
    init_sentry()

    environ["TZ"] = "Europe/Moscow"

    logger.info("Starting bot")

    config = Settings()
    router = setup_routers()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot_info = await bot.get_me()

    await db.connect()

    redis_client = init_redis(config.REDIS_URL)
    if not await redis_client.ping():
        logger.error("❌ Redis не отвечает!")
        sys.exit(1)
    logger.info("✅ Redis подключен")
    bot.custom = {"db": db}

    dp = Dispatcher(
        storage=redis_client.storage,
        config=config,
        bot_info=bot_info,
        db=db,
        fsm_timeout=300,
        redis_client=redis_client,
    )

    # --- ИНТЕГРАЦИЯ NEXUS SDK ---
    nexus_sdk = None
    nexus_secret = environ.get("NEXUS_APP_SECRET", "")
    nexus_url = environ.get("NEXUS_ENDPOINT_URL", "http://nexus-webhook:8000/events/app")

    if nexus_secret:
        try:
            from nexus_sdk import NexusSDK

            nexus_sdk = NexusSDK(
                endpoint_url=nexus_url, app_secret=nexus_secret, project_name="tarot_bot"
            )
            # 1. Регистрируем глобальный перехватчик исключений aiogram
            nexus_sdk.register_aiogram_error_handler(dp)
            # 2. Запускаем периодическую отправку пульса (Heartbeat) каждые 15 секунд
            nexus_sdk.start_heartbeat(interval_seconds=15)
            logger.info(
                "📡 Nexus SDK Observability initialized successfully (Heartbeat & Error Handler)"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Nexus SDK: {e}")
    else:
        logger.warning("⚠️ NEXUS_APP_SECRET is not set in environment. Nexus SDK is disabled.")
    # ----------------------------

    dp.include_routers(router)

    dp.update.middleware(SentryMiddleware())
    dp.update.middleware(ErrorHandlerMiddleware())
    dp.update.middleware(RateLimitMiddleware())
    dp.update.outer_middleware(LoggerMiddleware())

    dp.message.filter(ChatTypeFilter(chat_type=["private"]))

    try:
        logger.info(f"Bot {bot_info.full_name} started (@{bot_info.username}. ID: {bot_info.id})")
        await dp.start_polling(bot)
    finally:
        # Грациозно останавливаем фоновые процессы SDK при выключении бота
        if nexus_sdk:
            await nexus_sdk.close()
        await bot.session.close()
        await db.close()


def cli():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == "__main__":
    cli()
