import pytest

from app.bot.modules.youtube.childes.search.services.search import (
    search_youtube_service,
)
from app.bot.modules.youtube.childes.search.settings import settings


@pytest.mark.unit
@pytest.mark.asyncio
async def test_youtube_search_service_not_found(
    fake_logging_data, fake_youtube_service_empty
):

    result = await search_youtube_service.recieve(
        name_video="test",
        sort="relevance",
        logging_data=fake_logging_data,
        service=fake_youtube_service_empty,
        youtube_channel_url=settings.CHANNEL_URL,
        youtube_video_url=settings.VIDEO_URL,
        max_results=1,
    )

    assert result.error == "Не найдено ни одного видео по запросу"
    assert result.message is None
    assert result.status == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_youtube_search_service_http_errors(
    fake_logging_data, fake_youtube_service_http_errors
):

    result = await search_youtube_service.recieve(
        name_video="test",
        sort="relevance",
        logging_data=fake_logging_data,
        service=fake_youtube_service_http_errors,
        youtube_channel_url=settings.CHANNEL_URL,
        youtube_video_url=settings.VIDEO_URL,
        max_results=1,
    )

    assert result.error == "Ошибка при доступе к youtube"
    assert result.message is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_youtube_search_service_success(
    fake_logging_data, fake_youtube_service_success
):

    result = await search_youtube_service.recieve(
        name_video="test",
        sort="relevance",
        logging_data=fake_logging_data,
        service=fake_youtube_service_success,
        youtube_channel_url=settings.CHANNEL_URL,
        youtube_video_url=settings.VIDEO_URL,
        max_results=1,
    )

    assert isinstance(result.message, list)
    assert settings.VIDEO_URL.replace("{video_id}", "") in result.message[0]
