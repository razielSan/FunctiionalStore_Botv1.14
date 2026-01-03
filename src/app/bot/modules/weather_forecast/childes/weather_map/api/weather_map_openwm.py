from pathlib import Path
from typing import List, Dict, Protocol

from aiohttp import ClientSession

from app.core.response import NetworkResponseData
from app.error_handlers.network import error_handler_for_the_website
from app.bot.modules.weather_forecast.childes.weather_map.settings import settings
from app.core.response import NetworkResponseData, LoggingData


class WeatherMapOpenWMApi:
    async def get_weather_map(
        self,
        api_openweathermap: str,
        weather_layers: Dict,
        url_weather_map: str,
        path_to_weathermap: Path,
        session: ClientSession,
        logging_data: LoggingData,
        folium: object,
        location_weather: List[float] = settings.LOCATION_WEATHER,
        zoom=5,
        overlay=True,
        control=True,
        opacity=0.6,
    ) -> NetworkResponseData:
        """
        Возвращает карту погоды 
        
        Работа с сайтом https://openweathermap.org.
        Работа с библиотекой folium.

        Args:
            api_openweathermap (str): API для сайта openweathermap
            weather_layers (Dict): Словарь погодных слоёв OpenWeatherMap
            url_weather_map (str): URL для получения карт погоды
            path_to_weathermap: (Path): Путь до папки для сохранения карты погоды
            session (ClientSession): Сессия для запроса
            logging_data (LoggingData): Обьект класса LoggingData содержащий в себе логгеры
            и имя роутера
            folium (object): Обьект собирающий карту погоды
            location_weather (list): Стартовая локация (По умолчанию Москва [55.751244, 37.618423])
            zoom (int, optional): Стартовое увеличение (По умолчанию 5)
            overlay (bool, optional): Чтобы слои были поверх карты (По умолчани True)
            control (bool, optional): Чтобы слои можно было влючать/выключать(По умолчанию True)
            opacity (float, optional): Прозрачность от 0(прозрачный) до 1(непрозрачный) (По умолчанию 0.6)

        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
                - headers(dict | None): заголовки ответа
        """
        weather_map: NetworkResponseData = await error_handler_for_the_website(
            session=session,
            url=url_weather_map,
            data_type="BYTES",
            logging_data=logging_data,
        )

        if weather_map.error:
            return weather_map

        m: folium.Map = folium.Map(
            location=location_weather,
            zoom_start=zoom,
        )

        # Добавляем каждый слой
        for name, layer in weather_layers.items():
            folium.TileLayer(
                tiles=f"https://tile.openweathermap.org/map/{layer}/{{z}}/{{x}}/{{y}}.png?appid={api_openweathermap}",
                attr="OpenWeatherMap",
                name=name,
                overlay=overlay,  # чтобы слой был поверх базовой карты
                control=control,  # чтобы можно было включать/выключать
                opacity=opacity,  # прозрачность (0 — прозрачный, 1 — непрозрачный)
            ).add_to(m)

        # Добавляем управление слоями
        folium.LayerControl().add_to(m)

        # Сохраняем карту погоды
        m.save(path_to_weathermap)

        return NetworkResponseData(
            message=path_to_weathermap,
            status=200,
            url=weather_map.url,
            method=weather_map.method,
        )


class WeatherMapOpenWMApiProtocol(Protocol):
    async def get_weather_map(
        self,
        api_openweathermap: str,
        weather_layers: Dict,
        url_weather_map: str,
        path_to_weathermap: Path,
        session,
        logging_data,
        folium,
        location_weather: List = settings.LOCATION_WEATHER,
        zoom=5,
        overlay=True,
        control=True,
        opacity=0.6,
    ) -> NetworkResponseData:
        """Протокол для WeatherMapOpenWMAp"""


weather_map_openwm_api: WeatherMapOpenWMApi = WeatherMapOpenWMApi()
