from typing import List
from pathlib import Path

from aiogram import Dispatcher

from app.app_utils.logging import setup_bot_logging, init_loggers
from app.app_utils.filesistem import ensure_directories
from app.app_utils.keyboards import get_total_buttons_reply_kb
from app.app_utils.logging import get_loggers, LoggingData
from app.app_utils.module_loader.loader import (
    get_child_modules_settings_temp_folder,
    load_modules,
)
from app.settings.init_logging import app_settings
from app.core.modules_loader import ModuleInfo
from app.bot.core.bot import dp, telegram_bot
from app.bot.core.init_logging import logging_data, bot_settings, bot_error_logger
from app.bot.core.middleware.errors import RouterErrorMiddleware
from app.core.paths import APP_DIR


async def setup_bot() -> Dispatcher:
    """Подключает все необходимые компоненты для работы бота."""

    modules_path: Path = APP_DIR / "bot" / "modules"

    array_modules: List[ModuleInfo] = load_modules(
        dp=dp,
        modules_path=modules_path,
        error_logger=bot_error_logger,
        root_package="app.bot.modules",
    )
    # Список корневых модулей
    root_modules: List[ModuleInfo] = [module for module in array_modules if module.root]

    # Формируем клавиатуру для главного меню
    get_main_keyboards = get_total_buttons_reply_kb(
        list_text=[
            module.settings.MENU_REPLY_TEXT
            for module in root_modules
            if module.settings.SERVICE_NAME != "main"
        ],
        quantity_button=2,
    )

    modules_settings: List[str] = [
        model.settings.SERVICE_NAME for model in root_modules
    ]  # список из имен роутеров

    # Получаем список из имен для папки temp
    list_temp_folder_name: List[str] = get_child_modules_settings_temp_folder(
        module_path=modules_path,
        error_logger=bot_error_logger,
        root_package="app.bot.modules",
    )

    # формируем путь для папки temp
    list_path_to_temp_folder: List[Path] = [
        bot_settings.PATH_BOT_TEMP_FOLDER / name for name in list_temp_folder_name
    ]

    ensure_directories(
        bot_settings.PATH_BOT_TEMP_FOLDER,
        bot_settings.PATH_BOT_STATIC_FOLDER,
        *list_path_to_temp_folder,
    )  # создает нужные пути

    init_loggers(
        bot_name=bot_settings.BOT_NAME,
        setup_bot_logging=setup_bot_logging,
        log_format=app_settings.LOG_FORMAT,
        date_format=app_settings.DATE_FORMAT,
        base_path=app_settings.PATH_LOG_FOLDER,
        log_data=logging_data,
        list_router_name=modules_settings,
        bot_logging=False,
    )  # инициализируем логи

    await telegram_bot.set_my_commands(
        commands=bot_settings.LIST_BOT_COMMANDS  # Добавляет команды боту
    )  # Добавляет команды боту
    await telegram_bot.delete_webhook(
        drop_pending_updates=True
    )  # Игнорирует все присланные сообщение пока бот не работал

    for model in root_modules:
        # получаем обьект  LoggingData содержащий логгеры
        logging: LoggingData = get_loggers(
            router_name=model.settings.SERVICE_NAME,
            logging_data=logging_data,
        )

        # Подключаем middleware
        model.router.message.middleware(
            RouterErrorMiddleware(
                logger=logging.error_logger,
            )
        )
        model.router.callback_query.middleware(
            RouterErrorMiddleware(logger=logging.error_logger)
        )

        logging.info_logger.info(f"Middleware для {logging.router_name} подключен")

    return get_main_keyboards, dp
