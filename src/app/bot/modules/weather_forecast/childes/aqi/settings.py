from typing import Dict, Optional
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.settings.response import telegam_emogi


class ModuleSettings(BaseSettings):
    SERVICE_NAME: str = "weather_forecast.childes.aqi"
    MENU_REPLY_TEXT: str = "weather_forecast.childes.aqi"
    MENU_CALLBACK_TEXT: str = f"{telegam_emogi.digit_1} Уровень Загрязнения Воздуха"
    MENU_CALLBACK_DATA: str = "weather_forecast.childes.aqi"
    NAME_FOR_TEMP_FOLDER: str = "weather_forecast/childes/aqi"
    ROOT_PACKAGE: str = "app.bot.modules.weather_forecast.childes.aqi"

    APPID: Optional[str] = None
    ULR_GEOLOCATED_OPENWEATHERMAP: str = (
        "http://api.openweathermap.org/"
        "geo/1.0/direct?q={query}&limit=5&appid={appid}"
    )  # URL для получения геолокации
    URL_AIR_POLLUTION: str = (
        "http://api.openweathermap.org/"
        "data/2.5/air_pollution?lat={lat}&lon={lon}&appid={appid}"
    )  # URL для получения данных о загрязнении воздуха

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        extra="ignore",
    )


class WeatherAqiSettings:
    AIR_POLLUTION: Dict = {
        "so2": {
            "Хороший": [0, 20],
            "Справедливый": [20, 80],
            "Умеренный": [80, 250],
            "Бедный": [250, 350],
            "Очень плохо": [350, float("inf")],
            "translation": "диоксид серы",
            "emoji": "⚗️",
        },
        "pm10": {
            "Хороший": [0, 20],
            "Справедливый": [20, 50],
            "Умеренный": [50, 100],
            "Бедный": [100, 200],
            "Очень плохо": [200, float("inf")],
            "translation": "крупные частицы пыли",
            "emoji": "💨",
        },
        "pm2_5": {
            "Хороший": [0, 10],
            "Справедливый": [10, 25],
            "Умеренный": [25, 50],
            "Бедный": [59, 75],
            "Очень плохо": [75, float("inf")],
            "translation": "мелкодисперсные частицы",
            "emoji": "🌫️",
        },
        "o3": {
            "Хороший": [0, 60],
            "Справедливый": [60, 100],
            "Умеренный": [100, 140],
            "Бедный": [140, 180],
            "Очень плохо": [180, float("inf")],
            "translation": "озон",
            "emoji": "☀️",
        },
        "co": {
            "Хороший": [0, 4400],
            "Справедливый": [4400, 9400],
            "Умеренный": [9400, 12400],
            "Бедный": [12400, 15400],
            "Очень плохо": [15400, float("inf")],
            "translation": "оксид углерода",
            "emoji": "🔥",
        },
        "no2": {
            "Хороший": [0, 40],
            "Справедливый": [40, 70],
            "Умеренный": [70, 150],
            "Бедный": [150, 200],
            "Очень плохо": [200, float("inf")],
            "translation": "диоксид азота",
            "emoji": "🚗",
        },
    }  # Словарь с данными о компонентах загрязнения воздуха

    AQI: Dict = {
        1: "Хороший",
        2: "Удовлетворительный",
        3: "Средний",
        4: "Плохой",
        5: "Очень плохой",
    }  # Словарь индексов качества воздуха


aqi_settings = WeatherAqiSettings()
settings = ModuleSettings()
