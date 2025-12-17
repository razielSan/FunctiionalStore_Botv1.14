from typing import List, Optional
from pathlib import Path

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Общие настройки бота."""

    BOT_NAME: str = "bot"

    # Базовые пути для бота - вычисляются относительно этого файла
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent
    BOT_DIR: Path = ROOT_DIR / BOT_NAME


    # Пути уникальные для бота
    PATH_BOT_STATIC_FOLDER: Path = BOT_DIR / "static"
    PATH_BOT_TEMP_FOLDER: Path = BOT_DIR / "temp"
    PATH_LOG_FOLDER: Path = ROOT_DIR / "logs"
    PATH_BOT_LOG_FOLDER: Path = ROOT_DIR / "logs" / BOT_NAME
    
    LOG_FORMAT: str = (
        "[%(asctime)s] - %(module)s:%(lineno)s - [%(levelname)s - %(message)s]"
    )
    DATE_FORMAT: str = "%Y-%m-%D %H-%M-%S"

    TOKEN: Optional[str] = None
    LIST_BOT_COMMANDS: List[BotCommand] = [
        BotCommand(command="start", description="Меню бота")
    ]

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=BOT_DIR / ".env", extra="ignore"
    )
