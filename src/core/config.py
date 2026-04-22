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

    AI_PRIMARY_MODEL: str = "gemma-4-26b-a4b-it"
    AI_FALLBACK_MODEL: str = "gemma-4-31b-it"
    AI_TIMEOUT: float = 5.0
    AI_MAX_TOKENS: int = 400
    AI_TEMPERATURE: float = 0.9

    AI_CIRCUIT_BREAKER_THRESHOLD: int = 3
    AI_CIRCUIT_BREAKER_WINDOW: int = 60
    AI_CIRCUIT_BREAKER_COOLDOWN: int = 120

    AI_CACHE_TTL: int = 3600
    AI_CACHE_ENABLED: bool = True

    @property
    def pg_dump_cmd(self) -> str:
        """Собрать команду pg_dump из DATABASE_URL."""
        url = self.DATABASE_URL.replace("postgresql://", "")
        user_pass, host_port_db = url.split("@")
        user, password = user_pass.split(":")
        host_port, db = host_port_db.split("/")
        host = host_port.split(":")[0]

        return f"PGPASSWORD={password} pg_dump -h {host} -U {user} -d {db}"

    class Config:
        env_file = get_env_path()
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_db_url(self) -> str:
        return self.DATABASE_URL

settings = Settings()
