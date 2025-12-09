from typing import List
from pathlib import Path

from aiogram import Dispatcher
from app_utils.logging import setup_bot_logging, init_loggers
from bot.core.bot import dp, telegram_bot
from app_utils.filesistem import ensure_derictories
from bot.core.config import logging_data, bot_settings
from core.modules_loader import ModuleInfo
from settings.response import app_settings
from app_utils.keyboards import get_total_buttons_reply_kb
from bot.core.config import bot_error_logger, bot_warning_logger, bot_info_logger
from app_utils.logging import get_loggers, LoggingData
from bot.core.middleware.errors import RouterErrorMiddleware
from app_utils.modules import load_modules, get_child_modules_settings_temp_folder


async def setup_bot() -> Dispatcher:
    """Подключает все необходимые компоненты для работы бота."""

    array_modules: List[ModuleInfo] = load_modules(
        modules_path=Path("bot/modules"),
        error_logger=bot_error_logger,
    )

    # Список корневых модулей
    root_modules: List[ModuleInfo] = [module for module in array_modules if module.root]

    for module in root_modules:
        if getattr(module.router, "parent_router", None) is None:
            bot_info_logger.info(
                f"\n[Auto] Root router inculde into dp: {module.router}"
            )
            dp.include_router(module.router)
        else:
            bot_warning_logger.warning(
                f"\n[Auto] Root router already attached: {module.router}"
            )
        for mod in array_modules:
            if mod.parent == module.root:
                if getattr(mod.router, "parent_router", None) is None:
                    module.router.include_router(mod.router)
                    bot_info_logger.info(
                        f"\n[Auto] Child router inculded into {module.router}: {mod.router}"
                    )
                else:
                    bot_warning_logger.warning(
                        f"\n[Auto] Child router already attached: {mod.router}"
                    )
    # Формируем клавиатуру для главного меню
    get_main_keyboards = get_total_buttons_reply_kb(
        list_text=[
            module.settings.MENU_REPLY_TEXT
            for module in root_modules
            if module.settings.SERVICE_NAME != "main"
        ],
        quantity_button=1,
    )

    modules_settings: List[str] = [
        model.settings.SERVICE_NAME for model in root_modules
    ]  # список из имен роутеров

    # Получаем список из имен для папки temp
    list_temp_folder_name = get_child_modules_settings_temp_folder(
        module_path=Path("bot/modules/"),
        error_logger=bot_error_logger,
    )

    # формируем путь для папки temp
    list_path_to_temp_folder = [
        bot_settings.PATH_BOT_TEMP_FOLDER / name for name in list_temp_folder_name
    ]

    ensure_derictories(
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
