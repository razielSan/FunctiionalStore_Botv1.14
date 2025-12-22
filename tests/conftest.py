import logging

import pytest

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
