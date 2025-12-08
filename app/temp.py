Решил сделать поле NAME_TEMPT_TO_FOLDER в каждой модели для того чтобы в temp была папка для нужных модели данных типа картинки файлы аудио

from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "proxies"
    MENU_REPLY_TEXT: str = "👩‍💻 Получить Список Прокси"
    MENU_CALLBACK_TEXT: str = "proxies"
    MENU_CALLBACK_DATA: str = "proxies"
    NAME_FOR_TEMP_FOLDER: str = "proxies" 


settings = ModuleSettings()


Функция которая проходится по всем вложенным settings.py и берет оттуда NAME_FOR_TEMP_FOLDER

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
        print(settings_file, 44)

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
        print(settings, 123)
        if settings and hasattr(settings, "NAME_FOR_TEMP_FOLDER"):
            array_settings.append(settings.NAME_FOR_TEMP_FOLDER)

    return array_settings


Вызываю ее в bot/core/startup.py для создания папок в темp


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
        print(settings_file, 44)

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
        print(settings, 123)
        if settings and hasattr(settings, "NAME_FOR_TEMP_FOLDER"):
            array_settings.append(settings.NAME_FOR_TEMP_FOLDER)

    return array_settings


и папка temp теперь содержит

temp/
    example_model/
    example_model.features/
    main/
    proxies/
    proxies.mod_webshare
    
    
И когда удаляю модуль то ничего не ломается..


Да много из чего что предложил хочется реализовать
Заинтересовал 

1.генератор авто-документации
2. middleware для указания времени во время запроса
и все остальные =)

Так же подумал что можно замутить из командной строки чтобы модуль удалять а он удалял уже все логи
с ним связаныые и путь в папке temp допустим а не самому удалять