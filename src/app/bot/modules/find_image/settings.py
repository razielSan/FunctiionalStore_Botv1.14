from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "find_image"
    MENU_REPLY_TEXT: str = "🔎 Поиск Изображений"
    MENU_CALLBACK_TEXT: str = "find_image"
    MENU_CALLBACK_DATA: str = "find_image"
    NAME_FOR_TEMP_FOLDER: str = "find_image"
    ROOT_PACKAGE: str = "app.bot.modules.find_image"


settings = ModuleSettings()
