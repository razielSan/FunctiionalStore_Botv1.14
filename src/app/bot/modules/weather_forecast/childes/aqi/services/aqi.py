from typing import Dict, Union

from aiohttp import ClientSession
from app.core.response import LoggingData, NetworkResponseData, ResponseData

from app.bot.modules.weather_forecast.childes.aqi.api.aqi_openwm import (
    AqiOpenWMApiProtocol,
)
from app.error_handlers.decorator import safe_async_execution


class AqiService:
    async def recieve(
        self,
        city: str,
        api_openweathermap: str,
        url_geolocated_openweathermap,
        url_air_pollution: str,
        air_pollution: Dict,
        aqi: Dict,
        session: ClientSession,
        logging_data: LoggingData,
        aqi_openwm_api: AqiOpenWMApiProtocol,
    ) -> Union[NetworkResponseData, ResponseData]:
        """
        Application service для сценария отправки пользователю данных об уровне загрязнения воздуха.

        Отвечает за:
        - оркестрацию вызова AqiOpenWMApi
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI
        """
        decorator_function = safe_async_execution(logging_data=logging_data)
        func = decorator_function(aqi_openwm_api.get_air_pollution_city)

        result_aqi: NetworkResponseData = await func(
            city=city,
            api_openweathermap=api_openweathermap,
            url_air_pollution=url_air_pollution,
            url_geolocated_openweathermap=url_geolocated_openweathermap,
            air_pollution=air_pollution,
            aqi=aqi,
            session=session,
            logging_data=logging_data,
        )
        return result_aqi


aqi_service: AqiService = AqiService()
