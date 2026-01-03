from typing import Optional, Dict, List
import asyncio
from googleapiclient.errors import HttpError

from app.core.response import NetworkResponseData, LoggingData
from app.error_handlers.format import format_errors_message
from app.bot.modules.youtube.childes.search.api.search import search_youtube_api


class SearchYoutuveService:
    async def recieve(
        self,
        name_video: str,
        sort: str,
        logging_data: LoggingData,
        service: object,
        youtube_channel_url: str,
        youtube_video_url: str,
        max_results: int = 50,
        relevance_language: str = "ru",
    ) -> NetworkResponseData:
        """
        Application service для сценария поиска информации о видео.

        Отвечает за:
        - оркестрацию вызова YoutubeSearchAp
        - взаимодействие с googleapiclient
        - обработку ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:

            type_youtube: str = (
                "channel" if sort == "channel" else "video"
            )  # Определяем тип сортировки
            order_youtube: Optional[str] = (
                None if sort == "channel" else sort
            )  # Определяем критерии сортировки

            loop = asyncio.get_running_loop()

            try:  # отправляем запрос
                response_youtube: Dict = await loop.run_in_executor(
                    None,
                    lambda: service.search()
                    .list(
                        q=name_video,
                        part="snippet",
                        relevanceLanguage=relevance_language,
                        type=type_youtube,
                        maxResults=max_results,
                        order=order_youtube,
                    )
                    .execute(),
                )
            except HttpError as err:
                logging_data.error_logger.exception(
                    format_errors_message(
                        error_text=f"Youtube API error: {err}",
                        method="GET",
                        url="https://www.youtube.com/",
                        status=0,
                        name_router=logging_data.router_name,
                        function_name=SearchYoutuveService.recieve.__name__,
                    )
                )
                return NetworkResponseData(
                    error="Ошибка при доступе к youtube",
                    status=err.status_code,
                    method="GET",
                    url="https://www.youtube.com/",
                )

            response_youtube: Optional[List] = response_youtube.get("items", None)

            if not response_youtube:  # если список пустой
                return NetworkResponseData(
                    error="Не найдено ни одного видео по запросу",
                    status=200,
                    method="GET",
                    url="https://www.youtube.com/",
                )

            result_response: List[
                str
            ] = await search_youtube_api.get_description_video_by_youtube(
                response_youtube=response_youtube,
                youtube_channel_url=youtube_channel_url,
                youtube_video_url=youtube_video_url,
            )  # делаем запрос к api на получение списка с описаниями видео

            return NetworkResponseData(
                message=result_response,
                url="https://www.youtube.com/",
                status=200,
                method="GET",
            )
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    error_text=str(err),
                    method="GET",
                    url="https://www.youtube.com/",
                    status=0,
                    name_router=logging_data.router_name,
                    function_name=SearchYoutuveService.recieve.__name__,
                )
            )
            return NetworkResponseData(
                error="Ошибка на стороне сервера.Идет работа по исправлению...",
                status=0,
                url="https://www.youtube.com/",
                method="GET",
            )


search_youtube_service: SearchYoutuveService = SearchYoutuveService()
