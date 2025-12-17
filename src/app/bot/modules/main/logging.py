from functools import lru_cache

from app.app_utils.logging import get_loggers
from app.bot.core.config import logging_data
from app.core.response import LoggingData


@lru_cache()
def get_log() -> LoggingData:
    return get_loggers(
        router_name="main",
        logging_data=logging_data,
    )
