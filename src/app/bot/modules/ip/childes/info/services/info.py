from typing import Callable
from pathlib import Path

from app.error_handlers.decorator import safe_async_execution
from app.bot.modules.ip.childes.info.api.info import InfoApiProtocol


class InfoService:
    async def recieve(
        self,
        url: str,
        path_folder_flag_country: Path,
        path_folder_none_flag_img: Path,
        session,
        logging_data,
        info_api: InfoApiProtocol,
    ):
        """
        Application service для сценария выдачи информации по ip.

        Отвечает за:
        - оркестрацию вызова InfoApi
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI
        """
        decorator_function = safe_async_execution(logging_data=logging_data)
        func = decorator_function(info_api.get_ip_info)

        ip_info = await func(
            url=url,
            path_folder_flag_country=path_folder_flag_country,
            path_folder_none_flag_img=path_folder_none_flag_img,
            session=session,
            logging_data=logging_data,
        )
        return ip_info


info_service: InfoService = InfoService()
