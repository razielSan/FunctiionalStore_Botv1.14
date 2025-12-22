from pydantic import BaseModel

from app.settings.response import telegam_emogi


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "find_image.childes.find_name_image"
    MENU_REPLY_TEXT: str = "find_image.childes.find_name_image"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_1} По Названию"
    MENU_CALLBACK_DATA: str = "find_image.childes.find_name_image"
    NAME_FOR_TEMP_FOLDER: str = "find_image/childes/find_name_image"
    ROOT_PACKAGE: str = "app.bot.modules.find_image.childes.find_name_image"


settings: ModuleSettings = ModuleSettings()
