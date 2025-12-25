from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.response import telegam_emogi


class ModuleSettings(BaseSettings):
    SERVICE_NAME: str = "youtube.childes.search"
    MENU_REPLY_TEXT: str = "youtube.childes.search"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_1} Поиск"
    MENU_CALLBACK_DATA: str = "youtube.childes.search"
    NAME_FOR_TEMP_FOLDER: str = "youtube/childes/search"
    ROOT_PACKAGE: str = "app.bot.modules.youtube.childes.search"
    CALLBACK_PREFIX: str = "sort"
    END_PREFIX: str = (
        "youtube_end"  # префикс для инлайн клавиатуры для пролистывания результата
    )

    API_KEY: Optional[str] = None
    VIDEO_URL: str = "https://www.youtube.com/watch?v={video_id}"
    CHANNEL_URL: str = "https://www.youtube.com/channel/{channel_id}"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
    )


settings = ModuleSettings()
