from typing import Dict, Union

from aiohttp import ClientSession
from app.core.response import LoggingData
from app.bot.modules.weather_forecast.childes.weather.api.weather_open_wp import (
    WeatherOpenWPApiProtocol,
)
from app.error_handlers.decorator import safe_async_execution
from app.core.response import ResponseData, NetworkResponseData


class WeatherService:
    async def recieve(
        self,
        city: str,
        url_weather: str,
        url_geolocated_openweathermap: str,
        api_openweathermap: str,
        weather_translation: Dict,
        session: ClientSession,
        logging_data: LoggingData,
        weather_open_wp_api: WeatherOpenWPApiProtocol,
        future: bool = False,
    ) -> Union[ResponseData, NetworkResponseData]:
        """
        Application service для сценария поиска изображений по названию.

        Отвечает за:
        - оркестрацию вызова WeatherApi
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """

        decorator_function = safe_async_execution(logging_data=logging_data)
        func = decorator_function(
            weather_open_wp_api.get_data_weather_forecast_with_openweathermap
        )

        result_weather: Union[NetworkResponseData, ResponseData] = await func(
            city=city,
            url_weather=url_weather,
            url_geolocated_openweathermap=url_geolocated_openweathermap,
            logging_data=logging_data,
            future=future,
            api_openweathermap=api_openweathermap,
            weather_translation=weather_translation,
            session=session,
        )

        return result_weather


weather_service: WeatherService = WeatherService()
