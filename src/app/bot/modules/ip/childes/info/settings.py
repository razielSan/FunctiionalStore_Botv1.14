from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, IPvAnyAddress

from app.settings.response import telegam_emogi


class NetworkConifg(BaseModel):
    any_ip: IPvAnyAddress


class ModuleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        extra="ignore",
    )

    SERVICE_NAME: str = "ip.childes.info"
    MENU_REPLY_TEXT: str = "ip.childes.info"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_1} Общая Информация"
    MENU_CALLBACK_DATA: str = "ip.childes.info"
    NAME_FOR_TEMP_FOLDER: str = "ip/childes/info"
    ROOT_PACKAGE: str = "app.bot.modules.ip.childes.info"

    ACCESS_KEY: Optional[str] = None
    ULR_IP_INFO: str = "http://api.ipapi.com/api/{ip}?access_key={access_key}&hostname=1"  # url для получения информации о ip


settings = ModuleSettings()
