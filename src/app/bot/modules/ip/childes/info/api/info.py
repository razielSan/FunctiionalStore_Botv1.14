from typing import Dict, Protocol
from pathlib import Path

from aiohttp import ClientSession

from app.error_handlers.network import error_handler_for_the_website
from app.core.response import LoggingData
from app.core.response import NetworkResponseData


class InfoApi:
    async def get_ip_info(
        self,
        url: str,
        path_folder_flag_country: Path,
        path_folder_none_flag_img: Path,
        session: ClientSession,
        logging_data: LoggingData,
    ) -> NetworkResponseData:
        """
        Возвращает пользователю информацию по ip

        Работа с сайтом http://api.ipapi.com.

        Args:
            url (str): url для получения информации о ip
            path_folder_flag_country (Path): Путь до папки с флагами стран
            path_folder_none_flag_img (Path): Путь до изображения если флаг не найден
            session (ClientSession): Сессия для запроса
            logging_data: Обьект класса LoggingData содержащий в себе логгеры и
            имя роутера

        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (Any | None): List c путем до флага страны и строкой
                  с информацией по ip (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
                - headers (dict): Заголовки ответа.
        """

        # делаем зпроса на получение информации по ip
        response_ip: NetworkResponseData = await error_handler_for_the_website(
            session=session,
            url=url,
            logging_data=logging_data,
        )

        if response_ip.error:
            return response_ip

        data_response_ip: Dict = response_ip.message

        # Получаем код страны если страна найденна
        country_code: str = data_response_ip.get("country_code", None)

        # Формируем путь до картинки с флагом страны если есть
        if country_code:
            code: str = country_code.lower()
            full_path: Path = path_folder_flag_country / f"{code}.png"
        else:
            full_path: Path = path_folder_none_flag_img

        # Составляем данные по ip
        data_ip: str = (
            f"ip: {data_response_ip.get('ip', None)}\n"
            f"hostname: {data_response_ip.get('hostname', None)}\n"
            f"type: {data_response_ip.get('type', None)}\n"
            f"continent_code: {data_response_ip.get('continent_code', None)}\n"
            f"continent_name: {data_response_ip.get('continent_name', None)}\n"
            f"country_code: {data_response_ip.get('country_code', None)}\n"
            f"country_name: {data_response_ip.get('country_name', None)}\n"
            f"region_code: {data_response_ip.get('region_code', None)}\n"
            f"region_name: {data_response_ip.get('region_name', None)}\n"
            f"city: {data_response_ip.get('city', None)}\n"
            f"zip: {data_response_ip.get('zip', None)}\n"
            f"latitude: {data_response_ip.get('latitude', None)}\n"
            f"longitude: {data_response_ip.get('longitude', None)}\n"
            f"msa: {data_response_ip.get('msa', None)}\n"
            f"dma: {data_response_ip.get('dma', None)}\n"
            f"radius: {data_response_ip.get('radius', None)}\n"
            f"ip_routing_type: {data_response_ip.get('ip_routing_type', None)}\n"
            f"connection_type: {data_response_ip.get('connection_type', None)}\n"
            f"geoname_id: {data_response_ip['location'].get('geoname_id', None)}\n"
            f"capital: {data_response_ip['location'].get('capital', None)}\n"
            f"country_flag_emoji: {data_response_ip['location'].get('country_flag_emoji', None)}\n"
            f"country_flag_emoji_unicode: {data_response_ip['location'].get('country_flag_emoji_unicode', None)}\n"
            f"calling_code: {data_response_ip['location'].get('calling_code', None)}\n"
            f"is_eu: {data_response_ip['location'].get('is_eu', None)}\n"
        )
        return NetworkResponseData(
            message=[str(full_path), data_ip],
            status=200,
            url=url,
            method="GET",
        )


class InfoApiProtocol(Protocol):
    async def get_ip_info(
        self,
        url: str,
        path_folder_flag_country: Path,
        path_folder_none_flag_img: Path,
        session: ClientSession,
        logging_data: LoggingData,
    ) -> NetworkResponseData:
        """Протокол для InfoApi."""


info_api: InfoApi = InfoApi()
