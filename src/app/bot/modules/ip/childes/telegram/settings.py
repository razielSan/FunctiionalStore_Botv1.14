from pydantic import BaseModel

from app.settings.response import telegam_emogi


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "ip.childes.telegram"
    MENU_REPLY_TEXT: str = "ip.childes.telegram" 
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_2} API ID Telegram"
    MENU_CALLBACK_DATA: str = "ip.childes.telegram"
    NAME_FOR_TEMP_FOLDER: str = "ip/childes/telegram"
    ROOT_PACKAGE: str = "app.bot.modules.ip.childes.telegram"
    
settings = ModuleSettings()
    