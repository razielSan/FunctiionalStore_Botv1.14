from functools import lru_cache

from app_utils.logging import get_loggers
from bot.core.config import logging_data
from core.response import LoggingData


@lru_cache()
def get_log() -> LoggingData:
    return get_loggers(
        router_name="example_model",
        logging_data=logging_data,
    )
