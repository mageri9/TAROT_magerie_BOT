from pathlib import Path

from pydantic_settings import BaseSettings


def get_env_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int]
    DATABASE_URL: str = "sqlite:///database/db.db"

    class Config:
        env_file = get_env_path()
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_db_url(self) -> str:
        return self.DATABASE_URL

settings = Settings()
