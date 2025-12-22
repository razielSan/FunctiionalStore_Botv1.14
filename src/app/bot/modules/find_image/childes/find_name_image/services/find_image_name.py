from pathlib import Path
from typing import Union
import asyncio
import os

from aiogram.types import Message, ReplyKeyboardRemove

from app.bot.modules.find_image.childes.find_name_image.settings import settings
from app.bot.modules.find_image.childes.find_name_image.api.find_name_image import (
    find_name_img_api,
)
from app.core.response import NetworkResponseData, LoggingData, ResponseData
from app.settings.response import messages
from app.core.paths import APP_DIR
from app.app_utils.filesistem import (
    make_archive,
    delete_all_files_and_symbolik_link,
    delete_data,
)
from app.error_handlers.format import format_errors_message


class FindImageNameService:
    async def recieve(
        self,
        title_image: str,
        count_images: int,
        message: Message,
        logging_data: LoggingData,
    ) -> Union[ResponseData, NetworkResponseData]:
        """
        Application service для сценария поиска изображений по названию.

        Отвечает за:
        - оркестрацию вызова FindImageNameAPI
        - управление временными файлами
        - упаковку результатов в архив
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI,
        кроме вспомогательных сообщений пользователю.
        """
        await message.answer(
            f"{messages.WAIT_MESSAGE}",
            reply_markup=ReplyKeyboardRemove(),
        )

        # Временный Путь до архива с картинками
        path_archive: Path = (
            APP_DIR
            / "bot"
            / "temp"
            / Path(settings.NAME_FOR_TEMP_FOLDER)
            / str(message.from_user.id)
        )

        # Путь для сохранения архива
        path_save: Path = APP_DIR / "bot" / "temp" / settings.NAME_FOR_TEMP_FOLDER

        # Количество скаченных картинок
        crawler_download: int = 0

        # Формируем сообщения для отслеживания прогресса
        status_message: Message = await message.answer(
            f"📸 Загружено: {crawler_download} из {count_images}..."
        )

        # делаем запрос на поиск изоабражений и скачиваем их
        crawl_task = await find_name_img_api.finds_on_request_and_save_image(
            title=title_image,
            count=count_images,
            path=path_archive,
        )

        last_count: int = 0
        while not crawl_task.done():
            await asyncio.sleep(1)
            crawler_download = sum(
                len(files) for _, _, files in os.walk(path_archive)
            )  # Общее количество
            # изображений в папке
            if crawler_download != last_count:  # если изображение скачалось
                try:
                    await status_message.edit_text(
                        f"📸 Загружено: {crawler_download} из {count_images}..."
                    )
                    last_count = crawler_download
                except Exception:
                    pass

        result_crawler = await crawl_task

        # Если не возникла ошибка
        if result_crawler is None:
            if not crawler_download:  # если список пустой
                logging_data.info_logger.info(
                    format_errors_message(
                        name_router=logging_data.router_name,
                        method="GET",
                        status="<unknown>",
                        url="<icrawler>",
                        error_text="Не найденно ни одного изображения",
                        function_name=FindImageNameService.recieve.__name__,
                    )
                )
                return NetworkResponseData(
                    error="Не найденно ни одного изображения",
                    status=404,
                    url="<icrawler>",
                    method="GET",
                )

            await status_message.edit_text(
                f"✅ Готово! Загружено {crawler_download} изображений."
            )

            # создаем архив
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

            # удаляем все изображения из временной
            delete_all_files_and_symbolik_link(
                path_folder=path_archive,
                logging_data=logging_data,
            )

            # Удаляем временную папку для хранения изображений
            delete_data(
                list_path=[path_archive],
                warning_logger=logging_data.warning_logger,
            )
            return result_api
        else:
            return result_crawler


find_image_name_service: FindImageNameService = FindImageNameService()
