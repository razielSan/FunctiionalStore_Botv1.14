from typing import Dict, Optional, List, Protocol

from app.core.response import NetworkResponseData, LoggingData
from app.error_handlers.network import error_handler_for_the_website

from aiohttp import ClientSession


class WeatherOpenWMApi:
    async def get_data_weather_forecast(
        self,
        city: str,
        url_geolocated_openweathermap: str,
        url_weather: str,
        api_openweathermap: str,
        weather_translation: Dict,
        session: ClientSession,
        logging_data: LoggingData,
        future: bool = False,
    ) -> NetworkResponseData:
        """
        Возвращает информацию о текущей погоде или на 5 дней.


        Работа с сайтом https://openweathermap.org.

        Args:
            city (str): Город для которого нужно узнать информацию
            url_geolocated_openweathermap (str): URL для получения геолокации
            url_weather (str): Url прогноза погоды на 5 или 1 день
            api_openweathermap (str): API для сайта openweathermap
            weather_translation: (dict): Словарь для перевода прогноза погоды
            session (ClientSession): Сессия для запроса
            logging_data (LoggingData): Обьект класса LoggingData содержащий логгеры и
            имя роутера
            future (bool): Флаг для определния прогноза погоды на 5 дней.
            True - прогноз погоды на 5 дней
            False - текущий прогноз погоды



        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (Any | None): Строка с прогнозом погоды (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
                - headers (dict | None): заголовки запроса
        """

        # Получаем данные геолокации для города
        geolocated_response = await error_handler_for_the_website(
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
                method=geolocated_response.method,
                url=geolocated_response.url,
            )
        data_geolocated: Dict = geolocated_response.message[0]

        lat: float = data_geolocated["lat"]
        lon: float = data_geolocated["lon"]

        list_weather: List = []

        # url для получения прогноза погоды на 1 или 5 дней
        url_weather: str = url_weather.format(
            lat=lat,
            lon=lon,
            appid=api_openweathermap,
        )

        # Делаем запрос на получения прогнозоа погоды
        weather_response = await error_handler_for_the_website(
            session=session,
            url=url_weather,
            logging_data=logging_data,
        )
        if future:  # если на 5 дней
            for weather in weather_response.message["list"]:
                if weather["dt_txt"].find("12:00:00") != -1:
                    list_weather.append(weather)
        else:
            list_weather.append(weather_response.message)

        # if future
        array_weather_forecast: List = []

        for weather in list_weather:
            # Провереям есть ли описание погоды в ответе
            try:
                weather_main: str = weather["weather"][0]["main"]
                weather_desc: str = weather["weather"][0]["description"]
                weather_description = weather_translation[weather_main][weather_desc]
            except (KeyError, IndexError, TypeError):
                weather_description = None
            # температура по цельсию
            degree: float = weather["main"]["temp"] - 273.15
            feels_like: float = (
                weather["main"]["feels_like"] - 273.15
            )  # температура по ощущению
            pressure: int = weather["main"]["pressure"]  # давление гПа
            humidity: int = weather["main"]["humidity"]  # влажность %
            visibility: int = weather.get("visibility", 0)  # видимость m
            wind: float = weather["wind"]["speed"]  # скорость ветра м/c
            clouds: int = weather["clouds"]["all"]
            date: Optional[str] = weather.get("dt_txt", None)

            # Формируем данные для описания
            temperature: str = (
                f"Температура на {date}" if date else "Текущая температура"
            )
            weather_description: str = (
                f"{weather_description[1]} {weather_description[0].title()} {weather_description[1]} \n\n"
                if weather_description
                else ""
            )
            data_weather: str = (
                f"{temperature}\n\n{city}\n\n"
                f"{weather_description}"
                f"🌡 Температура: {round(degree)} °C\n"
                f"🌡 Температура по ощущению: {round(feels_like)} \n"
                f"📊 Давление: {pressure} Гпа\n"
                f"💧 Влажность: {humidity} %\n"
                f"👁️ Видимость: {visibility} м\n"
                f"🌬️ Cкорость ветра: {wind} м/с\n"
                f"☁️ Облачность: {clouds} %"
            )

            # Если текущий прогноз погоды возвращаем прогноз
            if not future:
                return NetworkResponseData(
                    message=data_weather,
                    status=200,
                    url=weather_response.url,
                    method=weather_response.method,
                )
            array_weather_forecast.append(data_weather)

        # Если прогноз погоды на 5 дней
        weather_data: str = "\n\n".join(array_weather_forecast)
        return NetworkResponseData(
            message=weather_data,
            status=200,
            url=weather_response.url,
            method=weather_response.method,
        )


class WeatherOpenWPApiProtocol(Protocol):
    async def get_data_weather_forecast_with_openweathermap(
        self,
        city: str,
        url_geolocated_openweathermap: str,
        url_future_openweathermap: str,
        url_current_openweathermap: str,
        api_openweathermap: str,
        weather_translation: Dict,
        session: ClientSession,
        logging_data: LoggingData,
        future: bool = False,
    ) -> NetworkResponseData:
        """Протокол для WeatherApi."""


weather_openwm_api: WeatherOpenWMApi = WeatherOpenWMApi()
