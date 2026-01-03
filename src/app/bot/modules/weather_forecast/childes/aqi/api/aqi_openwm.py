from typing import Dict, List, Protocol

from aiohttp import ClientSession

from app.error_handlers.network import error_handler_for_the_website
from app.core.response import NetworkResponseData
from app.core.response import LoggingData


class AqiOpenWMApi:
    async def get_air_pollution_city(
        self,
        city: str,
        api_openweathermap: str,
        url_geolocated_openweathermap,
        url_air_pollution: str,
        air_pollution: Dict,
        aqi: Dict,
        session: ClientSession,
        logging_data: LoggingData,
    ) -> NetworkResponseData:
        """
        Вовращает данные о уровне загрязнения воздуха.

        Работа с сайтом https://openweathermap.org.

        Args:
            city (str): Название города
            api_openweathermap (str): API для сайта openweathermap
            url_geolocated_openweathermap (str)): URL для получения геолокации
            url_air_pollution (str): URL для получения данных о загрязнении воздуха
            air_pollution (Dict): Cловарь с компенентами и данными о них
            aqi (Dict): Словарь с номерами и значениями индексов качества воздуха
            session (ClientSession): Сессия для запроса
            logging_data (LoggingData): Обьект класса LoggingData содержащий логгеры и
            имя роутера

        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (str | None): Строка с информацией об уровне
                  загрязнения воздуха (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
                - headers (dict | None): заголовки ответа
        """

        # Получаем геолокацию города
        geolocated_response: NetworkResponseData = await error_handler_for_the_website(
            session=session,
            url=url_geolocated_openweathermap,
            logging_data=logging_data,
        )
        if geolocated_response.error:
            return geolocated_response

        if not geolocated_response.message:
            return NetworkResponseData(
                error="Такого города не существует",
                status=geolocated_response.status,
                url=geolocated_response.url,
                method=geolocated_response.method,
            )

        data_geolocated: Dict = geolocated_response.message[0]
        lat: float = data_geolocated["lat"]
        lon: float = data_geolocated["lon"]

        url_air_pollution: str = url_air_pollution.format(
            lat=lat, lon=lon, appid=api_openweathermap
        )

        # Делаем запрос на получения данных уровня загрязнения воздуха
        aqi_response: NetworkResponseData = await error_handler_for_the_website(
            session=session, url=url_air_pollution, logging_data=logging_data
        )
        if aqi_response.error:
            return aqi_response

        # Получаем словарь с данными по уровню загрязнению воздуха для города
        data_aqii_city = aqi_response.message

        if not data_aqii_city:
            return NetworkResponseData(
                error=f"🌫️ Нет данных о загрязнении воздуха для {city}",
                status=aqi_response.status,
                url=aqi_response.url,
                method=aqi_response.method,
            )

        # Получаем числовое значение индекса загрязнение воздуха
        aqi_city: int = data_aqii_city["list"][0]["main"]["aqi"]

        data: str = f"🌫️ Уровень загрзянения воздуха 🌫️\n\n{city.title()}\n\n"

        air_aqi: str = f"🌡️ Индекс качества воздуха 🌡️\n\n{aqi[aqi_city]}\n\n"

        # Словарь содержащий компоненты и их содержание в воздухе для города
        components_dict: Dict = data_aqii_city["list"][0]["components"]

        list_components: List[str] = [data, air_aqi]

        # Проходимся по компонентам словаря индексов качества воздуха
        for component in air_pollution:

            # Текущее числовое значеие компонента для введенного города
            data = components_dict.get(component, None)
            if not data:
                continue

            # Проходимся по значениям и соответсвующим им числовым выражениям
            for desc, values in air_pollution[component].items():
                if isinstance(values[0], str):
                    break

                # Словарь с данными для компонента
                air_pollution_component: Dict = air_pollution[component]

                # Вычисляем значение компнента для по числовому выражению
                if values[0] <= data < values[1]:
                    data_copmponent: str = (
                        f"{air_pollution_component['emoji']}"  # Эмоджи для компонента
                        f" {component} ({air_pollution_component['translation']}): "  # Название компонента
                        f"{data} - {desc}\n"
                    )
                    list_components.append(data_copmponent)

        air_components: str = "".join(list_components)
        return NetworkResponseData(
            message=air_components,
            status=aqi_response.status,
            url=aqi_response.url,
            method=aqi_response.method,
        )


class AqiOpenWMApiProtocol(Protocol):
    async def get_air_pollution_city(
        self,
        city: str,
        api_openweathermap: str,
        url_geolocated_openweathermap,
        url_air_pollution: str,
        air_pollution: Dict,
        aqi: Dict,
        session: ClientSession,
        logging_data: LoggingData,
    ) -> NetworkResponseData:
        """Протокол для AqiOpenWMApi"""


aqi_openwm_api: AqiOpenWMApi = AqiOpenWMApi()
