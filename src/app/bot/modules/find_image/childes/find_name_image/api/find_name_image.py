import asyncio
import os

from aiogram.types import Message
from icrawler.builtin import BingImageCrawler

from app.core.response import NetworkResponseData, LoggingData
from app.error_handlers.helpers import run_safe_inf_executror
from app.error_handlers.format import format_errors_message


class FindImageNameAPI:
    async def finds_on_request_and_save_image(
        self,
        title: str,
        count: int,
        path: str,
    ):
        pass
        """
        Создает Task c обьектом BingImageCrawler и возврашает task..
        
        Работа с icrawler.

        Args:
            title (str): Имя картинки
            count (int): Количество изображений для скачивания
            path (str): Путь куда будут залиты изображения

        Returns:
            Task: возвращает Task для отслеживания прогресса.
        """

        # класс содержащий в себе общие данные для поиска изображений
        crawler: BingImageCrawler = BingImageCrawler(
            feeder_threads=2,  # Увеличиваем feeder
            parser_threads=3,  # Увеличиваем parser
            downloader_threads=12,  # Максимальное количество потоков загрузки
            storage={"root_dir": path},
        )

        loop = asyncio.get_running_loop()

        # формируем Task для отслеживания прогресса
        crawl_task = asyncio.create_task(
            run_safe_inf_executror(
                loop,
                crawler.crawl,
                keyword=title,
                max_num=count,
            )
        )

        return crawl_task


find_name_img_api: FindImageNameAPI = FindImageNameAPI()
