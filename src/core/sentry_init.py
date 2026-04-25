import sentry_sdk
from sentry_sdk.integrations.loguru import LoguruIntegration

from core.config import settings


def init_sentry():
    """Инициализация Sentry для мониторинга ошибок."""
    if not settings.SENTRY_DSN:
        return None

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[LoguruIntegration()],
    )

    from loguru import logger

    logger.info(f"✅ Sentry initialized ({settings.SENTRY_ENVIRONMENT})")
