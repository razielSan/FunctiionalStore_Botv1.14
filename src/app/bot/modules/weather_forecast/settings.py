from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "weather_forecast"
    MENU_REPLY_TEXT: str = "🌈 Погода"
    MENU_CALLBACK_TEXT: str = "weather_forecast"
    MENU_CALLBACK_DATA: str = "weather_forecast"
    NAME_FOR_TEMP_FOLDER: str = "weather_forecast"
    ROOT_PACKAGE: str = "app.bot.modules.weather_forecast"


settings = ModuleSettings()
