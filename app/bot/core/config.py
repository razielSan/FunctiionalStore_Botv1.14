from bot.settings.bot_settings import BotSettings
from app_utils.logging import LoggerStorage
from app_utils.logging import setup_bot_logging
from settings.response import app_settings

bot_settings: BotSettings = BotSettings()

logging_data: LoggerStorage = LoggerStorage()


bot_info_logger, bot_warning_logger, bot_error_logger = setup_bot_logging(
    bot_name=bot_settings.BOT_NAME,
    base_path=app_settings.PATH_LOG_FOLDER,
    log_format=app_settings.LOG_FORMAT,
    date_format=app_settings.DATE_FORMAT,
)
