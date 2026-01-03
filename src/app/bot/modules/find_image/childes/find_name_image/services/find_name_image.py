from pathlib import Path
from typing import Union, Callable, Awaitable, Optional

from app.core.response import NetworkResponseData, LoggingData, ResponseData
from app.app_utils.filesistem import (
    make_archive,
    delete_all_files_and_symbolik_link,
    save_delete_data,
)
from app.error_handlers.format import format_errors_message
from app.bot.modules.find_image.childes.find_name_image.adapters import (
    ImageSearchAdapter,
)


class FindNameImageService:
    async def recieve(
        self,
        title_image: str,
        logging_data: LoggingData,
        path_save: Path,
        adapter: ImageSearchAdapter,
        path_archive: Path,
        source: str,
        notify_progress: Callable[[int, int, bool], Awaitable[None]],
        count_images: Optional[int] = None,
    ) -> Union[ResponseData, NetworkResponseData]:
        """
        Application service для сценария поиска изображений по названию.

        Отвечает за:
        - оркестрацию вызова IcrawlerAdapter, GoogleAdapter
        - управление временными файлами
        - упаковку результатов в архив
        - удаление всех изображений из временной папки
        - удаление временной папки
        - подготовку данных для handlers
        - обработку ошибок

        Не содержит логики взаимодействия с Telegram UI.
        """

        result_adapter: Union[ResponseData, NetworkResponseData] = await adapter.start(
            title=title_image,
            count=count_images,
            path=path_archive,
            notify_progress=notify_progress,
            logging_data=logging_data,
            source=source,
        )
        if result_adapter.message or result_adapter.message == 0:
            if result_adapter.message == 0:  # если не найдено ни одного изображения
                logging_data.info_logger.info(
                    format_errors_message(
                        name_router=logging_data.router_name,
                        method="GET",
                        status="<unknown>",
                        url="<icrawler>",
                        error_text="Не найденно ни одного изображения",
                        function_name=FindNameImageService.recieve.__name__,
                    )
                )
                return NetworkResponseData(
                    error="🤷‍♀️ Не найденно ни одного изображения",
                    status=404,
                    url="<icrawler>",
                    method="GET",
                )

            result_api: ResponseData = make_archive(
                base_name=str(path_save / f"{title_image}"),
                format_archive="zip",
                root_dir=path_archive,
                base_dir=".",
                logging_data=logging_data,
            )

            # Если архив создался добавляем расширения для его удаления
            if result_api.message:
                result_api.message = path_save / f"{title_image}.zip"

            # удаляем все изображения из временной папки
            delete_all_files_and_symbolik_link(
                path_folder=path_archive,
                logging_data=logging_data,
            )

            # Удаляем временную папку для хранения изображений
            await save_delete_data(
                list_path=[path_archive],
                warning_logger=logging_data.warning_logger,
            )
            return result_api
        else:
            return result_adapter


find_name_image_service: FindNameImageService = FindNameImageService()
