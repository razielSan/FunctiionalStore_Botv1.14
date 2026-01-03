from pathlib import Path
from typing import Dict, List, Protocol, Union, Callable, Awaitable

from aiohttp import ClientSession

from app.core.response import LoggingData, NetworkResponseData, ResponseData
from app.error_handlers.network import error_handler_for_the_website
from app.app_utils.filesistem import (
    save_delete_data,
    delete_all_files_and_symbolik_link,
    make_archive,
)
from app.app_utils.network import get_and_save_image


class KinopoiskApi:
    async def get_list_posters(
        self,
        title: str,
        session: ClientSession,
        logging_data: LoggingData,
        headers: Dict,
        notify_progress: Callable[[int, int, bool], Awaitable[None]],
        url_search_video_name: str,
    ) -> NetworkResponseData:
        """
        Возвращает список содержащий url postera и название файла

        Работа с "https://api.kinopoisk.dev/"

        Args:
            title (str): Строка с именами фильмов
            session (ClientSession): сессия для запроса
            logging_data (LoggingData): Обьект класса LoggingData содержащий в себе логгеры
            и имя роутера
            headers (Dict): Cловарь с заголовками
            notify_progress (Callable): Функция для отслеживания прогресса скачивания
            url_search_video_name (str): Url для поиска видео

        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (Any | None): Список из url и имени постера (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
                - headers (dict): Заголовки ответа
        """
        # Создаем список с названиями фильмов
        list_title_films: List = title.split(".")
        list_url_films: List = []
        for title in list_title_films:
            list_url_films.append(url_search_video_name.format(limit=1, query=title))

        array_link_img_url: List = []

        # Делаем отображения прогресса скачивания
        download: int = 0
        count: int = len(list_url_films)

        poster_response = None
        for url in list_url_films:
            # Делаем запрос на получения постеров для фильма
            poster_response: NetworkResponseData = await error_handler_for_the_website(
                session=session,
                url=url,
                headers=headers,
                logging_data=logging_data,
            )
            if poster_response.error:  # если произошла ошибка - пропускаем итерацию
                continue
            poster = poster_response.message["docs"][0].get("poster", None)
            # Если постер существует для фильма
            if poster:
                # Обновляем прогресс скачивания
                download += 1
                try:
                    await notify_progress(
                        download=download,
                        count_images=count,
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
                full_name: str = f"{alternative_name}({name})-{year}".replace(":", "")
                array_link_img_url.append(
                    [
                        poster.get("url"),
                        full_name,
                    ]
                )
        return NetworkResponseData(
            message=array_link_img_url,
            method="GET",
            status=200,
            url="<unknwon>",
        )

    async def save_archive_and_delete_posters(
        self,
        array_link_img_url: List[List[str]],
        session: ClientSession,
        logging_data: LoggingData,
        path_image_folder: Path,
        path_archive: Path,
    ):
        """
        Сохраняет изображения в архив, удаляет изображения, удаляет временную папку
        для изображений.

        Работа с "https://api.kinopoisk.dev/"

        Args:
            array_link_img_url (List[List[str, str]]): Список содержащий в себе url и имя постера
            session (ClientSession): Сессия для запроса
            logging_data (_type_): Обьект класса LoggingData содержащий в себе логгеры и
            имя роутера
            path_image_folder (Path): Путь до папки с изображениями
            path_archive (Path): Путь до архива

        Returns:
             ResponseData: Объект с результатом запроса.

             Атрибуты ResponseData:
                 - message (Any | None): Путь до архива c расширением (если запрос прошёл успешно).
                 - error (str | None): Описание ошибки, если запрос завершился неудачей.
        """

        response_url = None
        save_image_count: int = 0  # счетчик сохраненных изображений
        for url in array_link_img_url:

            response_url: NetworkResponseData = await get_and_save_image(
                data_requests=url[0],
                path_img=path_image_folder / f"{url[1]}.jpg",
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
        response_archive = make_archive(
            base_name=path_archive,
            format_archive="zip",
            root_dir=path_image_folder,
            base_dir=".",
            logging_data=logging_data,
        )

        # Если архив был создан то передаем путь до архива c расширением
        if response_archive.message:
            response_archive.message = Path(f"{path_archive}.zip")

        # удаляем все изображения из папки
        delete_all_files_and_symbolik_link(
            path_folder=path_image_folder,
            logging_data=logging_data,
        )

        # удаляем временную папку для хранения изображений
        await save_delete_data(
            list_path=[path_image_folder],
            warning_logger=logging_data.warning_logger,
        )
        return response_archive


kinopoisk_api: KinopoiskApi = KinopoiskApi()


class KinopoiskApiProtocol(Protocol):
    """Протокол для KinopoiskApi."""

    async def get_list_posters(
        self,
        title: str,
        session: ClientSession,
        logging_data: LoggingData,
        headers: Dict,
        notify_progress,
        url_search_video_name,
    ) -> NetworkResponseData:
        pass

    async def save_archive_and_delete_posters(
        self,
        array_link_img_url,
        session,
        logging_data,
        path_image_folder,
        path_archive,
    ) -> Union[NetworkResponseData, ResponseData]:
        pass
