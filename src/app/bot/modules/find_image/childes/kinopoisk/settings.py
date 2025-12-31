from typing import Optional, Dict
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.response import telegam_emogi


class ModuleSettings(BaseSettings):
    SERVICE_NAME: str = "find_image.childes.kinopoisk"
    MENU_REPLY_TEXT: str = "find_image.childes.kinopoisk"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_2} Обложки Фильмов (Kinopoisk)"
    MENU_CALLBACK_DATA: str = "find_image.childes.kinopoisk"
    NAME_FOR_TEMP_FOLDER: str = "find_image/childes/kinopoisk"
    ROOT_PACKAGE: str = "app.bot.modules.find_image.childes.kinopoisk"

    API_KEY: Optional[str] = None
    URL_SEARCH_VIDEO_NAME: str = (
        "https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit={limit}&query={query}"
    )
    URL_SEARCH_UNIVERSAL_VIDEO: str = (
        "https://api.kinopoisk.dev/v1.4/movie?page=1&limit={limit}"
    )

    HEADERS: Dict = {
        "accept": "application/json",
        "X-API-KEY": None,
    }

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        extra="ignore",
    )


settings: ModuleSettings = ModuleSettings()
