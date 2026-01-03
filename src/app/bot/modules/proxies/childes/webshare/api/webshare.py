from typing import Dict, Protocol
import aiohttp

from app.core.response import NetworkResponseData, LoggingData
from app.error_handlers.network import error_handler_for_the_website


class WebshareAPI:
    @staticmethod
    async def get_proxies(
        url_config: str,
        url_proxeis_list: str,
        api_key: str,
        session: aiohttp.ClientSession,
        logging_data: LoggingData,
        timeout: int = 15
    ) -> NetworkResponseData:
        """
        Возврщает обьект ResponseData содержащий строку с 10 прокси.

        Сайт: https://www.webshare.io/

        Args:
            url_config (str): URL для получения данных о пользователе
            url_proxeis_list (str): URL для получения списка  прокси
            api_key (str): API ключ
            sesiion (aiohttp.ClinetSession): сессия для запроса
            logging_data (LoggindData): Обьект класса LoggingData содержащий в себе
            логгеры и имя роутера
            timeout (int): Таймаут для запроса. По дефолту 15

        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (Any | None): Строка с 10 прокси.(если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
        """
        # Делаем запрос на получение токена
        response_token: NetworkResponseData = await error_handler_for_the_website(
            session=session,
            url=url_config,
            headers={
                "Authorization": f"{api_key}",
            },
            logging_data=logging_data,
            timeout=timeout,
        )

        if response_token.error:
            return response_token

        token: Dict = response_token.message[
            "proxy_list_download_token"
        ]  # Получаем токен

        # Делаем запрос на получение прокси адресов
        response_proxies: NetworkResponseData = await error_handler_for_the_website(
            session=session,
            url=url_proxeis_list.format(token=token),
            data_type="TEXT",
            logging_data=logging_data,
        )
        if response_proxies.error:
            return response_proxies
        # Получаем список из адресо прокси
        proxies_list: str = response_proxies.message.split("\r\n")
        proxies_list.pop(-1)

        # Формируем строки содержащиую адреса прокси
        data: str = ""
        for proxy in proxies_list:
            ip, port, username, password = proxy.split(":")
            data += f"{username}:{password}@{ip}:{port}\n"

        return NetworkResponseData(
            message=data,
            status=response_proxies.status,
            method=response_proxies.method,
            url=response_proxies.url,
        )


class WebshareApiProtocol(Protocol):
    """Протокол для WebshareAPi"""

    async def get_proxies(
        url_config: str,
        url_proxeis_list: str,
        api_key: str,
        session: aiohttp.ClientSession,
        logging_data: LoggingData,
    ) -> NetworkResponseData:
        pass


webshare_api: WebshareAPI = WebshareAPI()
