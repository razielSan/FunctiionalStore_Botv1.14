from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "example_modul"
    MENU_REPLY_TEXT: str = "example_modul" 
    MENU_CALLBACK_TEXT: str = "example_modul"
    MENU_CALLBACK_DATA: str = "example_modul"
    NAME_FOR_TEMP_FOLDER: str = "example_modul"
    ROOT_PACKAGE: str = "app.bot.modules.example_modul"
    
settings = ModuleSettings()
    