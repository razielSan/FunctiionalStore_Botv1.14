from typing import List
from time import time

from fp.fp import FreeProxy, FreeProxyException
from app.core.response import NetworkResponseData, LoggingData
from app.error_handlers.format import format_errors_message
from app.settings.response import messages
from app.bot.modules.proxies.childes.free_proxy.settings import FreeProxyResponse


class FreeProxyAPI:
    def get_proxies(
        self,
        type_proxy: str,
        logging_data: LoggingData,
        list_data_proxies: List[FreeProxyResponse],
        free_proxy: FreeProxy,
        limit_time_seconds: int = 90,
    ) -> NetworkResponseData:
        """
        Возвращает обьект NetworkResponseData, содержащий работающие прокси.

        Работает с библиотекой free-proxy.

        Args:
            type_proxy (str): Тип прокси('http' или 'https')
            logging_data (LoggingData): Обьекта класса LoggingData содержащий в себе
            логгеры и имя роутера
            list_data_proxies (List[FreeProxyResponse]): Список содержащий в себе
            обьекты класса FreeProxyResponse с данными прокси для запроса
            free_proxy (FreeProxy): Класс FreeProxy для парсинга прокси
            limit_time_seconds (int, optional): Время отведенное на запрос
            в секундах. По умолчанию 120.

        Returns:
           NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (str | None): Строка содержащая работающие прокси (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
        """

        proxies_list: List[str] = []
        message_error = "unknown"

        # По умолчанию запрос идет на получение http прокси, вычисляем является ли
        # запрос для получение https прокси
        https_data: bool = True if type_proxy == "https" else False

        url: str = FreeProxy().url

        # Стартовае время для ограничения запроса по времени
        start_time: float = time()

        # Проходимся по данным прокси
        for proxy in list_data_proxies:
            try:

                # Проверяем не вышло ли время
                current_time: float = time() - start_time
                if current_time > limit_time_seconds:
                    break

                # делаем запрос на получение прокси
                result_proxy = free_proxy(
                    https=https_data,
                    rand=proxy.rand,
                    anonym=proxy.anonym,
                    elite=proxy.elite,
                ).get()

                # Формируем строку с данными о прокси
                str_proxies: str = (
                    f"{proxy.title.format(type_proxy=type_proxy)}\n{result_proxy}\n"
                )
                proxies_list.append(str_proxies)
            except FreeProxyException as err:
                logging_data.info_logger.info(f"No proxy found: {err}")
                message_error: str = "В настоящее время рабочих прокси-серверов нет.."
            except Exception as err:
                logging_data.error_logger.exception(
                    format_errors_message(
                        name_router=logging_data.router_name,
                        method="GET",
                        status=0,
                        url=url,
                        error_text=err,
                        function_name=FreeProxyAPI.get_proxies.__name__,
                    )
                )
                message_error = messages.SERVER_ERROR

        # Если есть хоть один работающий прокси
        if len(proxies_list) > 0:
            proxies_data: str = "\n".join(proxies_list)
            return NetworkResponseData(
                message=proxies_data, method="GET", url=url, status=200
            )
        else:
            return NetworkResponseData(
                error=message_error,
                status=0,
                method="GET",
                url=url,
            )


free_proxy_api: FreeProxyAPI = FreeProxyAPI()
