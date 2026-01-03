from typing import Union

from aiohttp import ClientSession

from app.error_handlers.decorator import safe_async_execution
from app.bot.modules.proxies.childes.webshare.api.webshare import WebshareApiProtocol
from app.core.response import NetworkResponseData, ResponseData, LoggingData


class WebshareService:
    async def recieve(
        self,
        api_key: str,
        url_config: str,
        url_proxies_list: str,
        logging_data: LoggingData,
        session: ClientSession,
        webshare_api: WebshareApiProtocol,
    ) -> Union[NetworkResponseData, ResponseData]:
        """
        Application service для сценария отправки пользователю списка прокси.

        Отвечает за:
        - оркестрацию вызова WebshareAPI
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI
        """

        #  Отлавливаем все возмоэжные ошибки
        decorator_function = safe_async_execution(
            logging_data=logging_data,
        )
        func = decorator_function(webshare_api.get_proxies)

        # Получаем прокси
        proxies_data: Union[NetworkResponseData, ResponseData] = await func(
            api_key=api_key,
            url_config=url_config,
            url_proxeis_list=url_proxies_list,
            session=session,
            logging_data=logging_data,
        )

        return proxies_data


webshare_service: WebshareService = WebshareService()
