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
        logging_data: LoggingData,
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

        result_crawler = await crawl_task
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
        logging_data: Optional[LoggingData] = None,
        notify_progress: Optional[Callable[[int, int, bool], Awaitable[None]]] = None,
    ) -> Union[NetworkResponseData, ResponseData]:

        loop = asyncio.get_running_loop()

        # формируем Task для отслеживания прогресса
        result_crawler = await run_safe_inf_executror(
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
        logging_data: str,
        source_count: int,
        notify_progress: Optional[Callable[[int, int, bool], Awaitable[None]]] = None,
    ) -> None:
        ...
