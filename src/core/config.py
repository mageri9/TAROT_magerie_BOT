from pathlib import Path
from pydantic_settings import BaseSettings


def get_env_path() -> Path:
    """Возвращает путь к .env файлу (на 3 уровня выше, в корне проекта)."""
    return Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    BOT_TOKEN: str

    ADMIN_IDS: list[int]

    DATABASE_URL: str = "sqlite:///database/db.db"

    REDIS_URL: str = "redis://localhost:6379/0"

    AITUNNEL_API_KEY: str = ""

    class Config:
        env_file = get_env_path()
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_db_url(self) -> str:
        return self.DATABASE_URL

settings = Settings()
