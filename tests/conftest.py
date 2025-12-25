import logging

import pytest
from googleapiclient.errors import HttpError

from app.core.response import LoggingData


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
