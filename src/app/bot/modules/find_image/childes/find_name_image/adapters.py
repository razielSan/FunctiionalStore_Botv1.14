from typing import Optional, Awaitable, Callable, Protocol, Union
from pathlib import Path
import asyncio
import os

from aiohttp import ClientSession

from app.bot.modules.find_image.childes.find_name_image.extensions import (
    Crawler,
    Google,
)
from app.error_handlers.helpers import run_safe_inf_executror
from app.core.response import NetworkResponseData, LoggingData, ResponseData
from app.app_utils.network import get_and_save_image
from app.app_utils.chek import is_valid_url


class IcrawlerAdapter:
    def __init__(self, crawler: Crawler):
        self.crawler = crawler

    async def start(
        self,
        title: str,
        count: int,
        path: Path,
        source: str,
        logging_data: Optional[LoggingData] = None,
        notify_progress: Optional[Callable[[int, int, bool], Awaitable[None]]] = None,
    ) -> Union[NetworkResponseData, ResponseData]:

        crawler = self.crawler.get_bing_image_crawler()
        loop = asyncio.get_running_loop()
        crawl_task = asyncio.create_task(
            run_safe_inf_executror(
                loop,
                crawler.crawl,
                keyword=title,
                max_num=count,
            )
        )

        last_count: int = 0
        crawler_download: int = 0  # Количество скаченных картинок
        while not crawl_task.done():
            await asyncio.sleep(1)
            crawler_download = sum(
                len(files) for _, _, files in os.walk(path)
            )  # Общее количество
            # изображений в папке
            if crawler_download != last_count:  # если изображение скачалось
                await notify_progress(
                    crawler_download=crawler_download,
                    count_images=count,
                    source=source,
                )

                last_count = crawler_download

        result_crawler: Optional[ResponseData] = await crawl_task

        if result_crawler is None:  # если не произошло ошибки
            # Сообщаем пользователю об успешном завершении поиска
            if notify_progress:
                await notify_progress(
                    complete=True,
                    crawler_download=crawler_download,
                    source=source,
                )
            return NetworkResponseData(
                message=crawler_download,
                status=200,
                url="<icrawler>",
                method="GET",
            )

        else:
            return result_crawler


class GoogleAdapter:
    def __init__(self, google: Google, session: ClientSession):
        self.google = google
        self.session = session

    async def start(
        self,
        title: str,
        count: int,
        path: Path,
        source: str,
        logging_data: LoggingData,
        notify_progress: Optional[Callable[[int, int, bool], Awaitable[None]]] = None,
    ) -> Union[NetworkResponseData, ResponseData]:

        loop = asyncio.get_running_loop()

        # формируем Task для отслеживания прогресса
        result_crawler: Optional[ResponseData] = await run_safe_inf_executror(
            loop,
            self.google.search_with_google_client,
        )
        if isinstance(result_crawler, list):  # если не было ошибки
            saved: int = 0  # для отслеживания прогресса
            for url in result_crawler[:count]:
                await asyncio.sleep(0.5)
                try:
                    url_image: str = url.get("link")  # получаем url
                    if not is_valid_url(url_image):
                        continue
                    # пробуем сохранить изображения
                    img: NetworkResponseData = await get_and_save_image(
                        data_requests=url_image,
                        logging_data=logging_data,
                        path_img=path / f"{title}_{saved}.jpg",
                        session=self.session,
                    )
                    if img.error:  # если ошибка пропускаем итерацию
                        continue

                    saved += 1

                    if notify_progress:  # обновляем прогресс
                        await notify_progress(
                            crawler_download=saved,
                            count_images=count,
                            source=source,
                        )
                except Exception:
                    pass
            # Сообщаем пользователю об успешном завершении поиска
            if notify_progress:
                await notify_progress(
                    complete=True,
                    crawler_download=saved,
                    source=source,
                )

            return NetworkResponseData(
                message=saved,
                url="<unknown>",
                method="GET",
                status=200,
            )
        else:
            return result_crawler


def get_images_adapter(
    *,
    source: str,
    google: Google = None,
    crawler: Crawler = None,
    session: ClientSession = None,
) -> Union[GoogleAdapter, IcrawlerAdapter]:
    """Фабрика для создания адаптеров для модели find_name_image."""
    if source == "google":
        return GoogleAdapter(google=google, session=session)
    elif source == "icrawler":
        return IcrawlerAdapter(crawler=crawler)


class ImageSearchAdapter(Protocol):
    async def start(
        self,
        title: str,
        count: int,
        path: Path,
        source_count: Union[Crawler, Google],
        logging_data: Optional[LoggingData] = None,
        notify_progress: Optional[Callable[[int, int, bool], Awaitable[None]]] = None,
    ) -> Union[NetworkResponseData, ResponseData]:
        """Протокол для адаптеров  модели find_name_image.

        Выполняет запрос на получение изображений, если запрос прошел успешно то скачивает
        изображения.Возвращает обьект класса NetworkResponseData содержащий количество
        скаченных изображений.
        Если запрос не прошел возращает обьект класса ResponseData содержащий ошибку.

        Args:
            title (str): Название изображения
            count (int): Количество изображений
            path (Path): Временный путь до архива с картинками
            logging_data (Optional[LoggingData]): Обьект класса LoggingData содержащий логи и
            имя роутера
            source_count (int): Источник, который будет скачивать изображенияю.
            Поддерживаются: Crawler, Google
            notify_progress (Optional[Callable[[int, int, bool], Awaitable[None]]], optional):
            функция для отслеживания прогресса

        Returns:
            NetworkResponseData: Объект с результатом запроса.

            Атрибуты NetworkResponseData:
                - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
                - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
                - url (str): URL, по которому выполнялся запрос.
                - method (str): HTTP-метод, использованный при запросе.
                - headers (dict): Заголовки ответа

            ResponseData: Объект с результатом запроса.
                - error: (str | None):  Описание ошибки, если запрос завершился неудачей.
                - message: (Any | Nonr): Количество скачанных изображений (если запрос прошёл успешно)
        """
