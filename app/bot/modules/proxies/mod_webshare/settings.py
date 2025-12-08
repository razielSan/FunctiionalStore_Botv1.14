from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "proxies.mod_webshare"
    MENU_REPLY_TEXT: str = "proxies.mod_webshare" 
    MENU_CALLBACK_TEXT: str = "💼 webshare"
    MENU_CALLBACK_DATA: str = "proxies.mod_webshare"
    NAME_FOR_TEMP_FOLDER: str = "proxies.mod_webshare"
    
settings = ModuleSettings()
    