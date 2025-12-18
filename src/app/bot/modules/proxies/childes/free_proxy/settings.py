from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "proxies.childes.free_proxy"
    MENU_REPLY_TEXT: str = "proxies.childes.free_proxy"
    MENU_CALLBACK_TEXT: str = "1⃣ free proxy"
    MENU_CALLBACK_DATA: str = "proxies.childes.free_proxy"
    NAME_FOR_TEMP_FOLDER: str = "proxies/childes/free_proxy"
    ROOT_PACKAGE: str = "app.bot.modules.proxies.childes.free_proxy"

    CALLBACK_PREFIX: str = "free-proxy "


settings = ModuleSettings()
