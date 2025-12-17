from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "proxies"
    MENU_REPLY_TEXT: str = "👩‍💻 Получить Список Прокси"
    MENU_CALLBACK_TEXT: str = "proxies"
    MENU_CALLBACK_DATA: str = "proxies"
    NAME_FOR_TEMP_FOLDER: str = "proxies"
    ROOT_PACKAGE: str = "app.bot.modules.proxies"
    
settings = ModuleSettings()
    