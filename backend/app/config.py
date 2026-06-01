import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv


load_dotenv()

_DEFAULT_ASYNC_DB = Path(__file__).resolve().parent.parent / "valora_async.db"


class Settings:
    app_name = "Valora API"
    api_prefix = "/api"
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{_DEFAULT_ASYNC_DB}",
    )
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    jwt_secret_key = os.getenv(
        "JWT_SECRET_KEY",
        "dev-only-valora-secret-change-before-production",
    )
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    jwt_refresh_token_expire_days = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )
    cors_origins = os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )

    @property
    def allowed_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
