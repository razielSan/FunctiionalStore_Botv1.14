from typing import List
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class FreeProxyResponse:
    rand: bool
    anonym: bool
    elite: bool
    title: str


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "proxies.childes.free_proxy"
    MENU_REPLY_TEXT: str = "proxies.childes.free_proxy"
    MENU_CALLBACK_TEXT: str = "1⃣ free proxy"
    MENU_CALLBACK_DATA: str = "proxies.childes.free_proxy"
    NAME_FOR_TEMP_FOLDER: str = "proxies/childes/free_proxy"
    ROOT_PACKAGE: str = "app.bot.modules.proxies.childes.free_proxy"

    CALLBACK_PREFIX: str = "free-proxy "

    LIST_DATA_PROXIES: List[FreeProxyResponse] = [
        FreeProxyResponse(
            rand=False,
            anonym=False,
            elite=False,
            title="Свежий {type_proxy} работающий прокси",
        ),
        FreeProxyResponse(
            rand=False,
            anonym=True,
            elite=False,
            title="Случайный {type_proxy} работающий прокси",
        ),
        FreeProxyResponse(
            rand=False,
            anonym=False,
            elite=False,
            title="Анонимный {type_proxy} работающий прокси",
        ),
        FreeProxyResponse(
            rand=False,
            anonym=False,
            elite=True,
            title="Элитный {type_proxy} работающий прокси",
        ),
    ]


settings = ModuleSettings()
