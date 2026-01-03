from typing import Dict, Union
from pathlib import Path

from aiohttp import ClientSession

from app.bot.modules.find_image.childes.kinopoisk.api.kinopoisk import (
    KinopoiskApiProtocol,
)

from app.core.response import LoggingData, ResponseData, NetworkResponseData
from app.settings.response import telegam_emogi
from app.error_handlers.decorator import safe_async_execution


class KinopoiskService:
    async def recieve(
        self,
        title: str,
        session: ClientSession,
        logging_data: LoggingData,
        headers: Dict,
        path_image_folder: Path,
        path_archive: Path,
        notify_progress,
        url_search_video_name,
        kinopoisk_api: KinopoiskApiProtocol,
    ) -> Union[ResponseData, NetworkResponseData]:
        """
        Application service для сценария поиска постеров с неофициального API Kinopoisk.

        Отвечает за:
        - взаимодействие с КinopoiskAPI
        - подготовку данных для handlers
        - обработку ошибок

        Не содержит логики взаимодействия с Telegram UI.
        """

        decorator_funtion = safe_async_execution(logging_data=logging_data)
        func = decorator_funtion(kinopoisk_api.get_list_posters)

        result_posters = await func(
            title=title,
            session=session,
            logging_data=logging_data,
            headers=headers,
            notify_progress=notify_progress,
            url_search_video_name=url_search_video_name,
        )
        if result_posters.error:
            return result_posters

        array_link_img_url = result_posters.message  # достаем данные из message

        if isinstance(array_link_img_url, list):
            if len(array_link_img_url) == 0:
                return NetworkResponseData(
                    error=f"{telegam_emogi.yellow_triangle_with_exclamation_mark} "
                    "Постеры для фильмов не найденны",
                    status=404,
                    url="<unknown>",
                    method="<unknown>",
                )
        await notify_progress(
            download=len(array_link_img_url),
            complete=True,
        )
        # Отправляем запрос на сохранение изображений в архив
        response_archive: Union[
            NetworkResponseData, ResponseData
        ] = await kinopoisk_api.save_archive_and_delete_posters(
            array_link_img_url=array_link_img_url,
            session=session,
            logging_data=logging_data,
            path_image_folder=path_image_folder,
            path_archive=path_archive,
        )
        return response_archive


kinopoisk_service: KinopoiskService = KinopoiskService()
