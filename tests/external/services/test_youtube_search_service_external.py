from pathlib import Path
from typing import List

from dotenv import dotenv_values
import pytest

from app.bot.modules.youtube.childes.search.services.search import (
    search_youtube_service,
)
from app.bot.modules.youtube.childes.search.extensions import get_service
from app.bot.modules.youtube.childes.search.settings import settings


API_KEY = dotenv_values(
    dotenv_path=Path(__file__).resolve().parent.parent.parent.parent
    / "src"
    / "app"
    / "bot"
    / "modules"
    / "youtube"
    / "childes"
    / "search"
    / ".env"
)["API_KEY"]


@pytest.mark.external
@pytest.mark.asyncio
async def test_youtube_search_service_success(
    fake_logging_data,
):

    service = get_service(api_key=API_KEY)

    result = await search_youtube_service.recieve(
        name_video="test",
        sort="relevance",
        logging_data=fake_logging_data,
        service=service,
        youtube_channel_url=settings.CHANNEL_URL,
        youtube_video_url=settings.VIDEO_URL,
        max_results=1,
    )

    assert result.error is None
    assert result.message is not None
    assert isinstance(result.message, List)
    assert len(result.message) == 1


@pytest.mark.external
@pytest.mark.asyncio
async def test_youtube_search_service_not_found(
    fake_logging_data,
):

    service = get_service(api_key=API_KEY)

    result = await search_youtube_service.recieve(
        name_video="...........................",
        sort="channel",
        logging_data=fake_logging_data,
        service=service,
        youtube_channel_url=settings.CHANNEL_URL,
        youtube_video_url=settings.VIDEO_URL,
        max_results=1,
    )

    assert result.error == "Не найдено ни одного видео по запросу"
    assert result.message is None
    assert result.status == 200
