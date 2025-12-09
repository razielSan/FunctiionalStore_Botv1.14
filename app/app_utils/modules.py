from typing import List, Dict, Callable
from pathlib import Path
from types import ModuleType
from logging import Logger
from core.response import InlineKeyboardData

from error_handlers.helpers import safe_import
from core.modules_loader import ModuleInfo

TEMPLATE_FILES: Dict[str, str] = {
    """__init__.py""": "# init for {name}\n",
    "router.py": """from aiogram import Router
    
    
router: Router = Router(name='{name}')

# Register handlres below    
    """,
    "settings.py": """from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "{name}"
    MENU_REPLY_TEXT: str = "{name}" 
    MENU_CALLBACK_TEXT: str = "{name}"
    MENU_CALLBACK_DATA: str = "{name}"
    NAME_FOR_TEMP_FOLDER: str = "{name}"
    
settings = ModuleSettings()
    """,
    "response.py": """# Responses, strings, text for module {name}
from pathlib import Path

from app_utils.modules import get_child_modules_settings_inline_data
from app_utils.keyboards import get_total_buttons_inline_kb

inline_data = get_child_modules_settings_inline_data(
    module_path=Path("{path_to_module}")
)

get_keyboards_menu_buttons = get_total_buttons_inline_kb(
    list_inline_kb_data=inline_data, quantity_button=1
)
""",
    "logging.py": """from functools import lru_cache

from app_utils.logging import get_loggers
from bot.core.config import logging_data
from core.response import LoggingData


@lru_cache()
def get_log() -> LoggingData:
    return get_loggers(
        router_name="{root_router_name}",
        logging_data=logging_data,
    )
    """,
}

TEMPLATATE_DIRS: List[str] = [
    "api",
    "fsm",
    "service",
    "utils",
    "handlers",
    "keyboards",
]


def create_module(
    list_name_modules: List,
    rel_path_to_modules: Path,
) -> None:
    """
    Создает модули и все вложенные модули

    Архитетура модуля:
    api/
    fsm/
    service/
    utils/
    keyboards/
    __init__.py
    router.py
    settings.py
    response.py
    logging.py

    Args:
        list_name_modules (List): Список из названий модулей.
        Если модуль вложен то название должно быть разделено знаком /

        Пример:
        ["video/main", "audio]

        Создаст:
            video/
                settings.py
                router.py
                ...
            video/main
                settings.py
                router.py
                ...
            audio/
                settings.py
                router.py


        rel_path_to_modules (Path): относительный путь до папки с модулями.
        Берется относительно директории app

        Пример:
        bot/modules
    """

    # Проходимся по именам модулей
    for name in list_name_modules:

        # Разделяем имя для добавление вложенных модулей
        parts: List[str] = name.replace("\\", "/").split("/")

        # Текущий путь
        current_path = rel_path_to_modules

        # Проходимся по вложенным именам
        for part in parts:

            # Формируем путь до модуля
            current_path: Path = current_path / part
            current_path.mkdir(parents=True, exist_ok=True)

            current_name = current_path.relative_to(rel_path_to_modules)
            current_name = current_name.as_posix().replace("/", ".")
            # Создаем фацлы
            for filename, content in TEMPLATE_FILES.items():
                file_path: Path = current_path / filename
                if not file_path.exists():
                    content = content.replace("{name}", current_name)
                    # для получения логов использоуем корневое имя роутера

                    content = content.replace(
                        "{root_router_name}", current_name.split(".")[0]
                    )
                    path_to_module = str(current_path).replace("\\", "/")
                    content = content.replace("{path_to_module}", path_to_module)
                    file_path.write_text(content)

            # Создаем папки
            for dir_name in TEMPLATATE_DIRS:
                directory: Path = current_path / dir_name
                directory.mkdir(exist_ok=True)
                init_file: Path = directory / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("# init\n")


def load_modules(
    modules_path: Path,
    error_logger: Logger,
) -> List[ModuleInfo]:
    """
    Проходится по всем папкам внутри переданного пути.

    Ищет внутри папок файлы router.py и settings.py.
    Внутри router.py ищет обьект router
    Внутри settings.py ищет обьект settings

    Если файлов settings.py или router.py идет дальше по папкам
    Если произошла ошибка импорта пишет в лог
    Возвращает List[ModuleInfo] содержащий в себе найденные обьекты settings и router
    если не находит пишет в лог

    Args:
        modules_path (Path): Относительный путь до нужного модуля

        Пример
        bot/modules/video

        error_logger (Logger): Логер для записи в лог ошибок

    Returns:
        List[ModuleInfo]: Обьект содержащий в себе settings и router

        Атрибуты ModuleInfo]:
            - root (str | None): Если роутер корневой будет указно его имя если нет None
            - settings (object): Обьект с настройками
            - router (object): Обьект router
            - parent (str | None): Если корневой роутер то будет None если child то имя
              корневого роутера
    """

    modules: List = []  # список из ModuleInfo

    # Проходися по всем файлам содержащим router.py
    for router_file in modules_path.rglob("router.py"):

        module_dir: Path = router_file.parent

        # ПРоверяем содержится ли в пути settings.py
        settings_file: Path = module_dir / "settings.py"
        if not settings_file.exists():
            continue

        # Относительный импорт
        import_module: str = (
            router_file.parent.with_suffix("").as_posix().replace("/", ".")
        )

        # Безопасно имопртируем settings b router
        settings_module = safe_import(
            f"{import_module}.settings",
            error_logger=error_logger,
        )

        if not settings_module:
            continue

        router_module = safe_import(
            f"{import_module}.router",
            error_logger=error_logger,
        )
        if not router_module:
            continue

        # Проверяем есть ли внутри settings и router данные
        settings = getattr(settings_module, "settings", None)
        router = getattr(router_module, "router", None)

        # вычисляем по rel_path_to_root - root_name и parent
        rel_path_to_root = (
            router_file.relative_to(modules_path).as_posix().split("/")
        )  # ["audio", "router.py"]

        # Проверяем являет ли router корневой или дочернем
        # Корневой(root_name="имя корневого роутера", parent=None)
        # Дочерний(root_name=None, parent="имя корневого роутера")
        root_name = rel_path_to_root[0] if len(rel_path_to_root) <= 2 else None
        parent = rel_path_to_root[0] if len(rel_path_to_root) > 2 else None

        if settings and router:
            modules.append(
                ModuleInfo(
                    root=root_name,
                    settings=settings,
                    router=router,
                    parent=parent,
                )
            )
        else:
            error_logger.error(
                f"[AUTO IMPORT ERROR] Обьекты {settings} и {router} не найдены"
            )

    return modules


def get_child_modules_settings_inline_data(
    module_path: Path,
    error_logger: Logger = None,
) -> List[InlineKeyboardData]:
    """
    Проходится по дочерним модулям из указанного пути по файлам settings.py.

    Записывает данные для инлайн клавиатуры в InlineKeyboardData

    Важное
    обьект settings должен содержать
    settings.MENU_CALLBACK_DATA
    settings.MENU_CALLBACK_TEXT

    Если

    Args:
        modules_path (Path): Относительный путь до нужного модуля

        Пример
        bot/modules/video

        error_logger (Logger) : Логер для записи в лог ошибок


    Returns:
        List[InlineKeyboardData]: Возвращает список из InlineKeyboardData

        Атрибуты InlineKeyboardData]:
                - text (str): текст инлайн клавиатуры
                - callback_data (str): callback_data инлайн клавиатуры
                - resize_keyboard (bool, Optional): Подгон размера клавиатуры.True по умолчанию
    """

    array_settings: List = []

    # Ищем по все дочерним модулям settings.py
    for settings_file in module_path.glob("*/settings.py"):
        # Пропускаем корневой settings.py самого модуля
        if settings_file.parent == module_path:
            continue

        # Относительный путь до модуля
        settings_import: str = (
            settings_file.parent.with_suffix("").as_posix().replace("/", ".")
        )

        # импортируем settings
        module_settings = safe_import(
            f"{settings_import}.settings",
            error_logger=error_logger,
        )
        if not module_settings:
            continue

        # Получаем settings из settings.py
        settings = getattr(module_settings, "settings", None)

        if (
            settings
            and hasattr(settings, "MENU_CALLBACK_DATA")
            and hasattr(settings, "MENU_CALLBACK_TEXT")
        ):
            array_settings.append(
                InlineKeyboardData(
                    text=settings.MENU_CALLBACK_TEXT,
                    callback_data=settings.MENU_CALLBACK_DATA,
                )
            )

    return array_settings


def get_child_modules_settings_temp_folder(
    module_path: Path,
    error_logger: Logger = None,
) -> List[str]:
    """
    Проходится по дочерним модулям из указанного пути по файлам settings.py.

    Важное
    Обьект settings должен содержать
    settings.NAME_FOR_TEMP_FOLDER

    Args:
        modules_path (Path): Относительный путь до нужного модуля

        Пример
        bot/modules/video

        error_logger (Logger) : Логер для записи в лог ошибок


    Returns:
        List[str]: Возвращает список из имен для папки temp

    """

    array_settings: List = []

    for settings_file in module_path.rglob("settings.py"):

        # Относительный путь до модуля
        settings_import: str = (
            settings_file.parent.with_suffix("").as_posix().replace("/", ".")
        )

        # импортируем settings
        module_settings = safe_import(
            f"{settings_import}.settings",
            error_logger=error_logger,
        )
        if not module_settings:
            continue

        # Получаем settings из settings.py
        settings = getattr(module_settings, "settings", None)
        if settings and hasattr(settings, "NAME_FOR_TEMP_FOLDER"):
            array_settings.append(settings.NAME_FOR_TEMP_FOLDER)

    return array_settings
