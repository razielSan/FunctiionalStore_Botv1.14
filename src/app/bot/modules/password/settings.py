from typing import List

from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "password"
    MENU_REPLY_TEXT: str = "🔒 Генератор Паролей"
    MENU_CALLBACK_TEXT: str = "password"
    MENU_CALLBACK_DATA: str = "password"
    NAME_FOR_TEMP_FOLDER: str = "password"
    ROOT_PACKAGE: str = "app.bot.modules.password"
    CALLBACK_PREFIX: str = "password"

    SIMPLE: str = "simple"
    DIFFICULT: str = "difficult"
    KEYBOARD_LAYOUT_ENGLISH: List[str] = [
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm",
        "qazwsxedcrfvtgbyhnujm",
    ]
    DIGITS: str = "0123456789"


settings = ModuleSettings()
