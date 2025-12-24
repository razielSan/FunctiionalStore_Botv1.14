import asyncio
from typing import List, Union
from asyncio import Task

from aiogram.types import Message

from app.bot.modules.proxies.childes.free_proxy.logging import get_log
from app.bot.modules.proxies.childes.free_proxy.api.free_proxy import free_proxy_api
from app.error_handlers.helpers import run_safe_inf_executror
from app.core.response import ResponseData, NetworkResponseData
from app.settings.response import messages


class FreePoxyService:
    async def recieve(
        self,
        type_proxy: str,
        message: Message,
    ) -> Union[NetworkResponseData, ResponseData]:
        """
        Application service для сценария поиска изображений по названию.

        Отвечает за:
        - оркестрацию вызова FreeProxyAPI
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI,
        кроме вспомогательных сообщений пользователю.
        """
        logging_data = get_log()

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
                90,
                logging_data=logging_data,
            )
        )
        # создаем сообщение для показывания прогресса запроса пользователю
        progress_message: Message = await message.answer(text=messages.WAIT_MESSAGE)

        progress_list: List[str] = [".", "..", "...", "....", "....."]
        count: int = 0

        # встаем в цикл пока не завершится запрос
        while not progress_task.done():
            if count > 4:
                count = 0
            try:
                await progress_message.edit_text(
                    text=f"{messages.WAIT_MESSAGE}{progress_list[count]}",
                )
            except Exception:
                pass
            count += 1

            await asyncio.sleep(1)

        msg = await progress_task
        return msg


free_proxy_service: FreePoxyService = FreePoxyService()
