from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Steam Market Analysis MVP"
    app_env: str = "dev"
    database_url: str = "sqlite:///./steam_market_mvp.db"
    default_source: str = "mock"
    cs2sh_api_key: str = ""
    cs2sh_base_url: str = "https://cs2.sh/api"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
