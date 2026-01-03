from typing import Dict, Union

from aiohttp import ClientSession
from app.core.response import LoggingData
from app.bot.modules.weather_forecast.childes.weather.api.weather_openwm import (
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
        weather_openwm_api: WeatherOpenWPApiProtocol,
        future: bool = False,
    ) -> Union[ResponseData, NetworkResponseData]:
        """
        Application service для сценария отправки пользователю прогноза погоды.

        Отвечает за:
        - оркестрацию вызова WeatherOpenWMApi
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """

        decorator_function = safe_async_execution(logging_data=logging_data)
        func = decorator_function(
            weather_openwm_api.get_data_weather_forecast
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
