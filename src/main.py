import asyncio
import sys

from loguru import logger
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from filters.chat_type import ChatTypeFilter

from core.router_manager import setup_routers
from core.config import Settings
from core.db import db
from core.logger import setup_logging
from core.redis import init_redis

from middlewares.error_handler import ErrorHandlerMiddleware
from middlewares.logger import LoggerMiddleware
from middlewares.rate_limit import RateLimitMiddleware


async def main():
    setup_logging()

    environ['TZ'] = 'Europe/Moscow'

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
    bot.custom = {
        "redis_client": redis_client,
        "db": db
    }

    dp = Dispatcher(
        storage=redis_client.storage,
        config=config,
        bot_info=bot_info,
        db=db,
        fsm_timeout=300,
        redis_client = redis_client
    )

    dp.include_routers(router)

    dp.update.middleware(RateLimitMiddleware())
    dp.update.middleware(ErrorHandlerMiddleware())
    dp.update.outer_middleware(LoggerMiddleware())

    dp.message.filter(ChatTypeFilter(chat_type=["private"]))

    try:
        logger.info(f'Bot {bot_info.full_name} started (@{bot_info.username}. ID: {bot_info.id})')
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await db.close()


def cli():
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")


if __name__ == '__main__':
    cli()
