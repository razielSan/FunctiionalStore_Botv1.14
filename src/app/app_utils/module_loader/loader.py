from typing import List
from pathlib import Path
from logging import Logger

from app.error_handlers.helpers import safe_import
from app.core.response import InlineKeyboardData
from app.core.modules_loader import ModuleInfo


def load_modules(
    dp,
    modules_path: Path,
    error_logger: Logger,
    root_package: str,
) -> List[ModuleInfo]:
    """
    Проходится по всем папкам внутри переданного пути.

    Ищет внутри папок файлы router.py и settings.py.
    Внутри router.py ищет обьект router
    Внутри settings.py ищет обьект settings

    Если файлов settings.py или router.py нет, то идет дальше по папкам
    Если произошла ошибка импорта пишет в лог

    Args:
        modules_path (Path): Путь до нужного модуля
        error_logger (Logger): Логгер для записи в лог ошибок
        root_package (str): Путь для импорта, начинается с корневой директории

        Пример:
        app.bot.modules

    Returns:
        List[ModuleInfo]: обьект содержащий в себе

        Атрибуты ModuleInfo]:
            - root (str | None): Если роутер корневой будет указно его имя если нет None
            - settings (object): Обьект с настройками
            - router (object): Обьект router
            - parent (str | None): Если корневой роутер то будет None если child то имя
              корневого роутера
    """
    try:
        modules: List = []  # список из ModuleInfo
        root_router: None = None  # корневой роутер текущего модуля
        # Проходимся по всем файлам содержащим router.py
        for router_file in modules_path.rglob("router.py"):
            module_dir: Path = router_file.parent
            # Проверяем содержится ли в пути settings.py
            settings_file: Path = module_dir / "settings.py"
            if not settings_file.exists():
                continue

            # Относительный импорт
            rel_path: Path = router_file.parent.relative_to(modules_path)
            import_module: str = (
                f"{root_package}.{rel_path.as_posix().replace('/', '.')}"
            )
            # Безопасно импортируем settings и router
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
            register = getattr(
                router_module, "register", None
            )  # для подключения роутера

            # вычисляем по rel_path_to_root - root_name и parent
            rel_path_to_root = module_dir.relative_to(
                modules_path
            ).parts  # ("audio"), ("audio", "childes", "create")

            # Проверяем являет ли router корневой или дочернем
            # Корневой(root_name="имя корневого роутера", parent=None)
            # Дочерний(root_name=None, parent="имя корневого роутера")
            root_name = rel_path_to_root[0] if len(rel_path_to_root) == 1 else None
            parent_name = rel_path_to_root[0] if len(rel_path_to_root) > 1 else None

            parent_router: bool = (
                True if parent_name else False
            )  # определяем является ли роутер дочерним
            if (
                not parent_router
            ):  # Если роутер не дочерним кладем root_router  корневой роутер
                root_router = router

            # если есть в файле есть register то подключаем роутер
            if register:
                register(
                    dp=dp,
                    parent_router=parent_router,
                    root_router=root_router,
                )

            if settings and router:
                modules.append(
                    ModuleInfo(
                        root=root_name,
                        settings=settings,
                        router=router,
                        parent=parent_name,
                    )
                )
            else:
                error_logger.error(
                    f"[AUTO IMPORT ERROR] Обьекты {settings} и {router} не найдены"
                )

        return modules
    except Exception as err:
        error_logger.exception(err)


def get_child_modules_settings_inline_data(
    module_path: Path,
    root_package: str,
    error_logger: Logger = None,
) -> List[InlineKeyboardData]:
    """
    Проходится по дочерним модулям из указанного пути по файлам settings.py.

    Записывает данные для инлайн клавиатуры в InlineKeyboardData.

    Важное: Обьект settings должен содержать

    settings.MENU_CALLBACK_DATA
    settings.MENU_CALLBACK_TEXT


    Args:
        module_path (Path): Путь до модуля
        error_logger (Logger): Логгер для записи в лог ошибок
        root_package (str): Путь для импорта до childes, начинается с корневой директории

        Пример:
        app.bot.modules.example_modul.childes


    Returns:
        List[InlineKeyboardData]: Возвращает список из InlineKeyboardData

        Атрибуты InlineKeyboardData]:
                - text (str): Текст инлайн клавиатуры
                - callback_data (str): Callback_data инлайн клавиатуры
                - resize_keyboard (bool, Optional): Подгон размера клавиатуры. True по умолчанию
    """

    array_settings: List = []

    # Ищем по папкам внутри пути
    for path in module_path.iterdir():
        # Если не папка то пропускаем
        if not path.is_dir():
            continue

        # Если в папке есть settings.py
        settings_path: Path = path / "settings.py"
        if settings_path.exists():

            rel_path: Path = settings_path.parent.relative_to(module_path)
            import_module: str = (
                f"{root_package}.{rel_path.as_posix().replace('/', '.')}"
            )

            module_settings = safe_import(
                module_path=f"{import_module}.settings",
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
    root_package: str,
    error_logger: Logger = None,
) -> List[str]:
    """
    Проходится по дочерним модулям из указанного пути по файлам settings.py.

    Важное: Обьект settings должен содержать
    
    settings.NAME_FOR_TEMP_FOLDER

    Args:
        module_path (Path): Путь до модуля
        error_logger (Logger) : Логгер для записи в лог ошибок
        root_package (str): Путь для импорта, начинается с корневой директории

        Пример:
        app.bot.modules


    Returns:
        List[str]: Возвращает список из имен для папки temp

    """

    array_settings: List = []

    for settings_file in module_path.rglob("settings.py"):

        # Путь до имени с модулем
        temp_path_name_with_point = (
            settings_file.parent.relative_to(module_path)
            .with_suffix("")
            .as_posix()
            .replace("/", ".")
        )  # video.childes.test

        settings_path: str = f"{root_package}.{temp_path_name_with_point}.settings"  # app.bot.modules.video.childes.test

        # импортируем settings
        module_settings = safe_import(
            module_path=settings_path,
            error_logger=error_logger,
        )
        if not module_settings:
            continue

        # Получаем settings из settings.py
        settings = getattr(module_settings, "settings", None)
        if settings and hasattr(settings, "NAME_FOR_TEMP_FOLDER"):
            array_settings.append(settings.NAME_FOR_TEMP_FOLDER)

    return array_settings
