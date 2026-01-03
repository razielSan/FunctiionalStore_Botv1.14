from typing import Optional, List
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.response import telegam_emogi


class ModuleSettings(BaseSettings):
    SERVICE_NAME: str = "find_image.childes.find_name_image"
    MENU_REPLY_TEXT: str = "find_image.childes.find_name_image"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_1} По Названию"
    MENU_CALLBACK_DATA: str = "find_image.childes.find_name_image"

    NAME_FOR_TEMP_FOLDER: str = "find_image/childes/find_name_image"
    ROOT_PACKAGE: str = "app.bot.modules.find_image.childes.find_name_image"

    GOOGLE_CX: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    IMAGE_SOURCES: List[str] = [
        "icrawler",
        "google",
    ]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        extra="ignore",
    )


settings: ModuleSettings = ModuleSettings()
