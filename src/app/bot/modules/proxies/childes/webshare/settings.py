from typing import Optional
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ModuleSettings(BaseSettings):
    SERVICE_NAME: str = "proxies.childes.webshare"
    MENU_REPLY_TEXT: str = "proxies.childes.webshare"
    MENU_CALLBACK_TEXT: str = "2⃣ webshare"
    MENU_CALLBACK_DATA: str = "proxies.childes.webshare"
    NAME_FOR_TEMP_FOLDER: str = "proxies/childes/webshare"

    ApiKey: Optional[str] = None
    URL_CONFIG: str = "https://proxy.webshare.io/api/v2/proxy/config/"  # url для получения данных о пользователе
    URL_PROXIES_LIST: str = (
        "https://proxy.webshare.io/api/v2/"
        "proxy/list/download/{token}/-/any/username/direct/-/"
    )  # url для получения списка  прокси

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        extra="ignore",
    )


settings: ModuleSettings = ModuleSettings()
