from functools import lru_cache

from app.app_utils.logging import get_loggers
from app.bot.core.init_logging import logging_data
from app.core.response import LoggingData


@lru_cache()
def get_log() -> LoggingData:
    return get_loggers(
        router_name="password",
        logging_data=logging_data,
    )
    