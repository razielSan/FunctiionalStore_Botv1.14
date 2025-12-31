from typing import List, Dict, Union
import uuid
from pathlib import Path

from aiogram.types import ReplyKeyboardRemove, Message
from aiohttp import ClientSession

from app.bot.modules.find_image.childes.kinopoisk.settings import settings
from app.core.paths import APP_DIR
from app.error_handlers.network import error_handler_for_the_website
from app.bot.modules.find_image.childes.kinopoisk.logging import get_log
from app.app_utils.network import get_and_save_image
from app.app_utils.filesistem import (
    make_archive,
    delete_all_files_and_symbolik_link,
    delete_data,
)
from app.core.response import LoggingData, ResponseData, NetworkResponseData


class KinopoiskService:
    async def recieve(
        self,
        title: str,
        message: Message,
        session: ClientSession,
        logging_data: LoggingData,
    ) -> Union[ResponseData, NetworkResponseData]:
        """
        Application service для сценария поиска постеров с неофициального API Kinopoisk.

        Отвечает за:
        - взаимодействие с неофициальным API Kinopoisk
        - управление временными файлами
        - упаковку результатов в архив
        - удаление всех изображений из папки
        - удаление временной папки
        - подготовку данных для handlers
        - обработку ошибок

        Не содержит логики взаимодействия с Telegram UI,
        кроме вспомогательных сообщений пользователю.
        """

        # Создаем список с названиями фильмов
        list_title_films: List = title.split(".")
        list_url_films: List = []
        for title in list_title_films:
            list_url_films.append(
                settings.URL_SEARCH_VIDEO_NAME.format(limit=1, query=title)
            )

        await message.answer(
            f"🔍 Ищу обложки по запросу: {title}...",
            reply_markup=ReplyKeyboardRemove(),
        )

        # Путь до сохранения изображений
        path_folder: Path = (
            APP_DIR
            / "bot"
            / "temp"
            / settings.NAME_FOR_TEMP_FOLDER
            / str(message.from_user.id)
        )

        name_archive: str = uuid.uuid4().hex

        # Путь до архива с картинками
        path_archive: Path = (
            APP_DIR / "bot" / "temp" / settings.NAME_FOR_TEMP_FOLDER / name_archive
        )

        # Формируем заголовок запроса
        HEADERS: Dict = settings.HEADERS.copy()
        HEADERS["X-API-KEY"] = settings.API_KEY

        array_link_img_url: List = []

        # Делаем отображения прогресса скачивания
        download: int = 0
        count: int = len(list_url_films)
        msg: str = "📸 Полученно ссылок {} из {}..."
        status_message: Message = await message.answer(
            text=msg.format(
                download,
                count,
            )
        )

        logging_data: LoggingData = get_log()

        poster_response = None
        for url in list_url_films:
            # Делаем запрос на получения постеров для фильма
            poster_response: NetworkResponseData = await error_handler_for_the_website(
                session=session,
                url=url,
                headers=HEADERS,
                logging_data=logging_data,
            )
            if poster_response.error:  # если произошла ошибка - пропускаем итерацию
                continue
            poster = poster_response.message["docs"][0].get("poster", None)
            # Если постер существует для фильма
            if poster:
                # Обновляем прогресс скачивания
                download += 1
                if download % 2 == 0 or download == count:
                    try:
                        await status_message.edit_text(
                            msg.format(
                                download,
                                count,
                            )
                        )
                    except Exception:
                        pass

                # Формируем  данные для названия изображения
                name: str = poster_response.message["docs"][0]["name"]
                alternative_name = poster_response.message["docs"][0].get(
                    "alternativeName", "Нет"
                )
                year = poster_response.message["docs"][0].get("year", "Неизвестно")

                # формируем полное имя изобраежния без расширения
                full_name = f"{alternative_name}({name})-{year}".replace(":", "")
                array_link_img_url.append(
                    [
                        poster.get("url"),
                        full_name,
                    ]
                )
        if not array_link_img_url:
            return NetworkResponseData(
                error="Постеры для фильмов не найденны",
                status=404,
                url=getattr(poster_response, "url", "<unknown>"),
                method=getattr(poster_response, "method", "GET"),
            )

        # Сохраняем картинки и получаем список с путями до картинок

        response_url = None
        save_image_count: int = 0  # счетчик сохраненных изображений
        for url in array_link_img_url:

            response_url: NetworkResponseData = await get_and_save_image(
                data_requests=url[0],
                path_img=path_folder / f"{url[1]}.jpg",
                session=session,
                logging_data=logging_data,
            )
            # если произошла ошибка пропукскаем цикл
            if response_url.error:
                continue
            save_image_count += 1
        # Если не сохранились ни одно изображение то отправляем ошибку
        if save_image_count == 0:
            return response_url

        #  Создаем архив
        response_archive: ResponseData = make_archive(
            base_name=path_archive,
            format_archive="zip",
            root_dir=path_folder,
            base_dir=".",
            logging_data=logging_data,
        )

        # Если архив был создан то передаем путь до архива c расширением
        if response_archive.message:
            response_archive.message = (
                APP_DIR
                / "bot"
                / "temp"
                / settings.NAME_FOR_TEMP_FOLDER
                / f"{name_archive}.zip"
            )

        # удаляем все изображения из папки
        delete_all_files_and_symbolik_link(
            path_folder=path_folder,
            logging_data=logging_data,
        )

        # удаляем временную папку для хранения изображений
        delete_data(
            list_path=[path_folder],
            warning_logger=logging_data.warning_logger,
        )
        return response_archive


kinopoisk_service: KinopoiskService = KinopoiskService()
