from pathlib import Path
from typing import List, Optional, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.response import telegam_emogi


class ModuleSettings(BaseSettings):
    SERVICE_NAME: str = "weather_forecast.childes.weather_map"
    MENU_REPLY_TEXT: str = "weather_forecast.childes.weather_map"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_3} Карта Погоды"
    MENU_CALLBACK_DATA: str = "weather_forecast.childes.weather_map"
    NAME_FOR_TEMP_FOLDER: str = "weather_forecast/childes/weather_map"
    ROOT_PACKAGE: str = "app.bot.modules.weather_forecast.childes.weather_map"

    NAME_WEATHER_MAP: str = "weather_map.html"
    LOCATION_WEATHER: List[float] = [
        55.751244,
        37.618423,
    ]  # Список координат для города Москва
    WEATHER_LAYERS: Dict = {
        "Температура": "temp_new",
        "Облака": "clouds_new",
        "Осадки": "precipitation_new",
        "Давление": "pressure_new",
        "Ветер": "wind_new",
    }  # Список погодных слоёв OpenWeatherMap
    APPID: Optional[str] = None
    URL_WEATHER_MAPS: str = (
        "https://tile.openweathermap.org/" "map/temp_new/0/0/0.png?appid={appid}"
    )  # URL для получения карт погоды

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        extra="ignore",
    )


settings = ModuleSettings()
