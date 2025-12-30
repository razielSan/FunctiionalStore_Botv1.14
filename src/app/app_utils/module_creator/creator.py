from typing import List, Dict
from pathlib import Path
import traceback

from app.core.response import ResponseData


TEMPLATE_FILES: Dict[str, str] = {
    """__init__.py""": "# init for {name}\n",
    "router.py": """from pathlib import Path
from importlib import import_module

from aiogram import Router, Dispatcher
    
from app.bot.core.init_logging import bot_info_logger, bot_warning_logger  
    
    
router: Router = Router(name='{name}')

# Register router

def register(
    dp: Dispatcher,
    parent_router: bool,
    root_router: object,
) -> None:
    if not parent_router:  # если роутер корневой
        # Проверка на то что этот роутер ни к кому не подключен
        if getattr(router, "parent_router", None) is None:
            dp.include_router(router)
            bot_info_logger.info(
                "\\n[Auto] Root router inculde into dp: {}".format(router)
            )
        else:
            bot_warning_logger.warning(
                "\\n[Auto] Root router already attached: {}".format(router)
            )

    else:
        if getattr(router, "parent_router", None) is None:
            root_router.include_router(router)
            bot_info_logger.info(
                "\\n[Auto] Child router inculded into {}: {}".format(root_router, router)
            )
        else:
            bot_warning_logger.warning(
                "\\n[Auto] Child router already attached: {}".format(router)
            )
            
# Include sub router            
current_dir = Path(__file__).resolve().parent
handlers_path = current_dir / "handlers"
            
for file in handlers_path.glob("*.py"):
    if file.name == "__init__.py":
        continue

    module_name = f"{__package__}.handlers.{file.stem}"
    module = import_module(module_name)

    handler_router = getattr(module, "router", None)

    if handler_router:
        router.include_router(handler_router)
        bot_info_logger.info(
            "\\n[Auto] Sub router inculde into {}: {}".format(router, handler_router)
        )  
    """,
    "settings.py": """from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "{name}"
    MENU_REPLY_TEXT: str = "{name}" 
    MENU_CALLBACK_TEXT: str = "{name}"
    MENU_CALLBACK_DATA: str = "{name}"
    NAME_FOR_TEMP_FOLDER: str = "{temp_path}"
    ROOT_PACKAGE: str = "{root_package}"
    
settings = ModuleSettings()
    """,
    "response.py": """# Responses, strings, text for module {name}
from pathlib import Path

from app.app_utils.module_loader.loader import get_child_modules_settings_inline_data
from app.app_utils.keyboards import get_total_buttons_inline_kb


inline_data = get_child_modules_settings_inline_data(
    module_path=Path("{path_to_module}"),
    root_package="{root_childes}"
)

get_keyboards_menu_buttons = get_total_buttons_inline_kb(
    list_inline_kb_data=inline_data, quantity_button=1
)
""",
    "logging.py": """from functools import lru_cache

from app.app_utils.logging import get_loggers
from app.bot.core.init_logging import logging_data
from app.core.response import LoggingData


@lru_cache()
def get_log() -> LoggingData:
    return get_loggers(
        router_name="{root_router_name}",
        logging_data=logging_data,
    )
    """,
    "extensions.py": "# Plug-in extensions are below"
}

TEMPLATATE_DIRS: List[str] = [
    "api",
    "fsm",
    "services",
    "utils",
    "handlers",
    "keyboards",
    "childes",
]


def create_module(
    list_path_modules: List[str],
    module_path: Path,
    root_package: str,
) -> ResponseData:
    """
    Создает модуль и все вложенные модули

    Архитектура модуля:
    
    api/
    fsm/
    services/
    utils/
    keyboards/
    childes/
    __init__.py
    extensions.py
    router.py
    settings.py
    response.py
    logging.py

    Args:
        list_path_modules (List[str]): Список из названий путей модулей.
        Если модуль дочерний, то название должно быть разделено childes/

        Пример:
        ["video/childes/main", "audio]

        Создаст:
            video/
                childes/__init__.py
                __init__.py
                settings.py
                router.py
                ...
            video/childes/main/
                childes/__init__.py
                __init__.py
                settings.py
                router.py
                ...
            audio/
                childes/__init__.py
                __init__.py
                settings.py
                router.py
                ...


        path_to_modules (Path): путь до папки с модулями
        root_package (str): Путь для импорта, начинается с корневой директории

        Пример:
        app.bot.modules

    Returns:
        RepsonseData: объект содержащий в себе

        Атрибуты ResponseData:
            - message (Any | None): Содержание ответа. None если произошла ошибка
            - error (str | None): Текст ошибки если есть если нет то None
    """

    try:
        # Проверка на childes
        for name in list_path_modules:

            # Разделяем имя для добавления вложенных модулей
            parts: List[str] = name.replace("\\", "/").split("/")

            if parts[-1].lower() == "childes":
                return ResponseData(
                    error="childes используется для дочерних модулей. Укажите другое имя модуля",
                    message=None,
                )

            for index, folder_name in enumerate(parts, start=1):
                if index % 2 == 0:
                    if folder_name != "childes":
                        return ResponseData(
                            error="Разделитель между именами модулей должен называться - childes",
                            message=None,
                        )

        # Проходимся по именам модулей
        for name in list_path_modules:

            # Разделяем имя для добавление вложенных модулей
            parts: List[str] = name.replace("\\", "/").split("/")

            # Текущий путь
            current_path = module_path
            # Проходимся по вложенным именам
            for part in parts:
                # Формируем путь до модуля
                current_path: Path = current_path / part

                # если папка childes то пропускаем
                if part == "childes":
                    continue

                current_path.mkdir(parents=True, exist_ok=True)

                current_name = current_path.relative_to(module_path)
                current_name_with_point = current_name.as_posix().replace("/", ".")
                # Создаем файлы
                for filename, content in TEMPLATE_FILES.items():
                    file_path: Path = current_path / filename
                    if not file_path.exists():
                        content = content.replace("{name}", current_name_with_point)

                        # для получения логов использоуем корневое имя роутера
                        content = content.replace(
                            "{root_router_name}", current_name_with_point.split(".")[0]
                        )

                        # для получения инлайн клавиатуры для модуля
                        # используем текущий путь с добавлнеием childes - bot/modules/audio/childes
                        path_to_module = str(current_path / "childes").replace(
                            "\\", "/"
                        )
                        content = content.replace("{path_to_module}", path_to_module)

                        # Корневой путь для инлайн клавиатуры с добавлением childes
                        root_childes = (
                            f"{root_package}.{current_name_with_point}.childes"
                        )
                        content = content.replace(
                            "{root_childes}", root_childes
                        )  # app.bot.modules.audio.childes

                        # корневой путь для импортя модулей в настройках
                        rpg = f"{root_package}.{current_name_with_point}"
                        content = content.replace(
                            "{root_package}", rpg
                        )  # app.bot.modules.audio

                        # Для получения пути для папки temp используем текущее имя - audio/childes/create
                        content = content.replace(
                            "{temp_path}", str(current_name).replace("\\", "/")
                        )

                        file_path.write_text(content, encoding="utf-8")

                # Создаем папки
                for dir_name in TEMPLATATE_DIRS:
                    directory: Path = current_path / dir_name
                    directory.mkdir(exist_ok=True)
                    init_file: Path = directory / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text("# init\n")

        return ResponseData(
            error=None,
            message="module create",
        )
    except Exception:
        error: str = traceback.format_exc()
        return ResponseData(
            error=error,
            message=None,
        )


def creates_new_modules_via_the_command_line(
    list_path_modules: List[str],
    module_path: Path,
    root_package: str,
) -> None:
    """
    Создает новые модули для бота через командную строку.

    Дочерний модуль должен быть разделен 'childes' от родительского модуля.
    Пример:

    cli add-module video video/childes/create audio

    args:
        list_path_modules(List[str]): Список из имен путей модулей
        
        Пример
        ['video/childes/main', "audio"]
        
        module_path (Path):  Путь до папки с модулями
        root_package (str): Путь для импорта, начинается с корневой директории

        Пример:
        app.bot.modules

    """
    data: ResponseData = create_module(
        list_path_modules=list_path_modules,
        module_path=module_path,
        root_package=root_package,
    )
    if data.error:
        print(data.error)
    else:
        print(f"Modules {', '.join(list_path_modules)} created successfully")
