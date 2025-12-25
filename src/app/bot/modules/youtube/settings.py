from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "youtube"
    MENU_REPLY_TEXT: str = "▶ Youtube" 
    MENU_CALLBACK_TEXT: str = "youtube"
    MENU_CALLBACK_DATA: str = "youtube"
    NAME_FOR_TEMP_FOLDER: str = "youtube"
    ROOT_PACKAGE: str = "app.bot.modules.youtube"
    
settings = ModuleSettings()
    