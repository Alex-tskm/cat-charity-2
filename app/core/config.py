# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    database_url: str | None = None

    secret_key: str = 'fallback-secret-change-me'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
