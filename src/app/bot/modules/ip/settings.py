from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "ip"
    MENU_REPLY_TEXT: str = "💻 Информация По IP" 
    MENU_CALLBACK_TEXT: str = "ip"
    MENU_CALLBACK_DATA: str = "ip"
    NAME_FOR_TEMP_FOLDER: str = "ip"
    ROOT_PACKAGE: str = "app.bot.modules.ip"
    
settings = ModuleSettings()
    