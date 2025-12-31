import logging

import pytest
import pytest_asyncio
from googleapiclient.errors import HttpError
from fp.fp import  FreeProxyException
import aiohttp


from app.core.response import LoggingData


@pytest_asyncio.fixture
async def session():
    """Создает и предоставляет асинхронную сессию для каждого теста."""
    async with aiohttp.ClientSession() as session:
        yield session  # Предоставляем сессию тестовой функции


@pytest.fixture
def fake_logging_data():
    logger = logging.getLogger("test")
    logger.addHandler(logging.NullHandler())

    return LoggingData(
        router_name="test",
        error_logger=logger,
        warning_logger=logger,
        info_logger=logger,
    )


@pytest.fixture
def fake_youtube_service_empty():
    class FakeYoutubeService:
        def search(self):
            return self

        def list(self, **kwargs):
            return self

        def execute(self):
            return {"items": None}

    return FakeYoutubeService()


@pytest.fixture
def fake_youtube_service_http_errors():
    class FakeResp:
        status = 403
        reason = "Forbidden"

    class FakeYoutubeService:
        def search(self):
            return self

        def list(self, **kwargs):
            return self

        def execute(self):
            raise HttpError(resp=FakeResp(), content=b"quota exceeded")

    return FakeYoutubeService()


@pytest.fixture
def fake_youtube_service_success():
    class FakeYoutubeSearch:
        def search(self):
            return self

        def list(self, **kwargs):
            return self

        def execute(
            self,
        ):
            return {
                "items": [
                    {
                        "id": {"videoId": "abc123"},
                        "snippet": {
                            "title": "Test video",
                            "description": "Test description",
                        },
                    }
                ]
            }

    return FakeYoutubeSearch()


@pytest.fixture
def fake_free_proxy():
    class FakeFreeProxy:
        def __init__(
            self,
            https,
            rand,
            anonym,
            elite,
        ):
            self.https = https
            self.rand = rand
            self.anonym = anonym
            self.elite = elite

        def get(self):
            return "https" if self.https is True else "http"

    return FakeFreeProxy


@pytest.fixture
def fake_free_proxy_error():
    class FakeFreeProxyError:
        def __init__(
            self,
            https,
            rand,
            anonym,
            elite,
        ):
            self.https = https
            self.rand = rand
            self.anonym = anonym
            self.elite = elite

        def get(self):
            raise FreeProxyException(message="test")

    return FakeFreeProxyError
