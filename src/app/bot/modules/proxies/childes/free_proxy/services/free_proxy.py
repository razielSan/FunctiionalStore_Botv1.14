import asyncio
from typing import List, Union, Callable, Awaitable
from asyncio import Task

from aiogram.types import Message
from fp.fp import FreeProxy


from app.bot.modules.proxies.childes.free_proxy.logging import get_log
from app.bot.modules.proxies.childes.free_proxy.api.free_proxy import free_proxy_api
from app.bot.modules.proxies.childes.free_proxy.settings import FreeProxyResponse
from app.error_handlers.helpers import run_safe_inf_executror
from app.core.response import ResponseData, NetworkResponseData, LoggingData
from app.settings.response import messages


class FreePoxyService:
    async def recieve(
        self,
        type_proxy: str,
        list_data_proxies: List[FreeProxyResponse],
        get_free_proxy: FreeProxy,
        logging_data: LoggingData,
        notify_progress: Callable[[str], Awaitable[None]] = None,
    ) -> Union[NetworkResponseData, ResponseData]:
        """
        Application service для сценария поиска прокси.

        Отвечает за:
        - оркестрацию вызова FreeProxyAPI
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """

        loop = asyncio.get_running_loop()

        # Формируем Task для отслеживания прогресса
        progress_task: Task[
            Union[ResponseData, NetworkResponseData]
        ] = asyncio.create_task(
            run_safe_inf_executror(
                loop,
                free_proxy_api.get_proxies,
                type_proxy,
                logging_data,
                list_data_proxies,
                get_free_proxy,
                90,
                logging_data=logging_data,
            )
        )
        # progress_message: Message = await message.answer(text=messages.WAIT_MESSAGE)

        progress_list: List[str] = [".", "..", "...", "....", "....."]
        count: int = 0

        # встаем в цикл пока не завершится запрос
        while not progress_task.done():
            if count > 4:
                count = 0

            # Обновляем прогресс скачивания
            if notify_progress:
                await notify_progress(
                    text=f"{messages.WAIT_MESSAGE}{progress_list[count]}",
                )

            count += 1

            await asyncio.sleep(1)

        msg: Union[ResponseData, NetworkResponseData] = await progress_task
        return msg


free_proxy_service: FreePoxyService = FreePoxyService()
