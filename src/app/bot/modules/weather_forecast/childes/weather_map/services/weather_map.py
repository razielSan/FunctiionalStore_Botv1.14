from pathlib import Path
from typing import Dict, Union

from aiohttp import ClientSession
from app.core.response import LoggingData, NetworkResponseData, ResponseData

from app.bot.modules.weather_forecast.childes.weather_map.api.weather_map_openwm import (
    WeatherMapOpenWMApiProtocol,
)
from app.error_handlers.decorator import safe_async_execution


class WeatherMapService:
    async def recieve(
        self,
        api_openweathermap: str,
        weather_layers: Dict,
        url_weather_map: str,
        path_to_weathermap: Path,
        session: ClientSession,
        logging_data: LoggingData,
        folium: object,
        weather_map_openwm_api: WeatherMapOpenWMApiProtocol,
        zoom: int = 5,
        overlay: bool = True,
        control: bool = True,
        opacity: float = 0.6,
    ) -> Union[NetworkResponseData, ResponseData]:
        """
        Application service для сценария отправки пользователю карты погоды.

        Отвечает за:
        - оркестрацию вызова WeatherMapOpenWMApi
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI
        """
        decorator_function = safe_async_execution(logging_data=logging_data)
        func = decorator_function(weather_map_openwm_api.get_weather_map)

        result_weather_map: NetworkResponseData = await func(
            api_openweathermap=api_openweathermap,
            weather_layers=weather_layers,
            url_weather_map=url_weather_map,
            path_to_weathermap=path_to_weathermap,
            folium=folium,
            session=session,
            logging_data=logging_data,
            zoom=zoom,
            overlay=overlay,
            control=control,
            opacity=opacity,
        )
        return result_weather_map


weather_map_service: WeatherMapService = WeatherMapService()
