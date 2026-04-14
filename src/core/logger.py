import sys
from pathlib import Path
from loguru import logger

def setup_logging():
    """Настройки логирования в файлы и консоль."""
    logger.remove()

    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Файл с ротацией
    logger.add(
        logs_dir / "bot_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        compression="gz",
        level="DEBUG",
        encoding="utf-8"
    )

    # Файл только для ошибок
    logger.add(
        logs_dir / "errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="14 days",
        level="ERROR",
        encoding="utf-8"
    )

    # Консоль
    logger.add(sys.stderr, level="INFO")