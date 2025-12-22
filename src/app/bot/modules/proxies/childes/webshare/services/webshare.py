from app.bot.modules.proxies.childes.webshare.logging import get_log
from app.error_handlers.decorator import safe_async_execution
from app.bot.modules.proxies.childes.webshare.api.webshare import webshare_api
from app.bot.modules.proxies.childes.webshare.settings import settings
from app.core.response import NetworkResponseData


class WebshareService:
    async def receive(self, session) -> NetworkResponseData:
        """
        Application service для сценария поиска изображений по названию.

        Отвечает за:
        - оркестрацию вызова WebshareAPI
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI
        """
        log = get_log()

        #  Отлавливаем все возмоэжные ошибки
        decorator_function = safe_async_execution(
            logging_data=log,
        )
        func = decorator_function(webshare_api.get_proxies)

        # Получаем прокси
        proxies_data = await func(
            api_key=settings.ApiKey,
            url_config=settings.URL_CONFIG,
            url_proxeis_list=settings.URL_PROXIES_LIST,
            session=session,
            logging_data=log,
        )

        return proxies_data


webshare_service: WebshareService = WebshareService()
