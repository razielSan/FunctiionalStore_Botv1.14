from typing import Tuple, Optional, List
from pathlib import Path
from logging import Logger
import shutil
import os
import asyncio

from app.core.response import ResponseData, LoggingData
from app.error_handlers.format import format_errors_message
from app.settings.response import telegam_emogi


def ensure_directories(
    *args: Path,
    info_logger: Optional[Logger] = None,
) -> None:
    """
    Проверяет наличие переданных путей и создает их при необходимости.

    Args:
        info_logger (Optional[Logger], optional): Логгер для записи в лог. Defaults to None.
    """
    requiered_dirs: Tuple[Path, ...] = args

    for dir in requiered_dirs:
        dir.mkdir(parents=True, exist_ok=True)
        if info_logger:
            info_logger.info(f"Директория {dir} создана")


def delete_all_files_and_symbolik_link(
    path_folder: Path,
    logging_data: LoggingData,
) -> None:
    """
    Удаляет все файлы в папке.

    Args:
        path_folder (Path): Путь до папки
        logging_data (LoggingData): Обьект класса LoggingData содержащий в себе логгеры и
        имя роутера
    """
    # Проверяем есть ли папка в наличии
    if not path_folder.exists():
        return

    for filename in os.listdir(path_folder):
        try:
            filepath: str = os.path.join(path_folder, filename)
            if os.path.isfile(filepath) or os.path.islink(filepath):
                os.remove(filepath)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    method="<unknown>",
                    status=0,
                    url="<unknown>",
                    error_text=str(err),
                    function_name=delete_all_files_and_symbolik_link.__name__,
                )
            )


async def save_delete_data(
    list_path: List[Path],
    warning_logger: Optional[Logger] = None,
    retries: int = 3,
) -> None:
    """Удаляет данные по переданному пути.

    Args:
        list_path (List[Path]): Список с путями до данных
        warning_logger (Optional[Logger], optional): логгер для записи в лог. По умолчанию None
        retries (int): Количество попыток для удаления данных
    """
    for path in list_path:
        for _ in range(retries):
            try:
                if path.is_file():
                    path.unlink()
                if path.is_dir():
                    shutil.rmtree(path=path)

            except PermissionError:
                await asyncio.sleep(1)
            except Exception as err:
                message: str = f"Ошибка при удалении {path}: {err}"
                if warning_logger:
                    warning_logger.exception(msg=message)


def make_archive(
    base_name: str,
    format_archive: str,
    root_dir: Path,
    base_dir: str,
    logging_data: LoggingData,
) -> ResponseData:
    """
    Создает архив по переданному пути.

    Args:
        base_name (str): Путь сохранения архива.Содержит в себе имя архива без расширения

        Пример
        app/bot/temp/video/video

        format_archive (str): Формат архива
        root_dir (Path): Путь к файлам которые нужно архивировать
        base_dir (str): Каталог, откуда начинается архивирование

        Пример
        "." - архивирует все файлы в сам архив без создания папок

        logging_data (LoggingData): Обьект класса LoggingData содержащий в себе логгеры и
        имя роутера

    Returns:
        ResponseData: Объект с результатом запроса.

        Атрибуты ResponseData:
            - message (str | None): Путь сохранения архива (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
    """
    try:
        shutil.make_archive(
            base_name=base_name,
            format=format_archive,
            root_dir=root_dir,
            base_dir=base_dir,
        )
        return ResponseData(message=base_name, error=None)
    except Exception as err:
        logging_data.error_logger.exception(
            format_errors_message(
                name_router=logging_data.router_name,
                method="<unknown>",
                status=0,
                url="<unknown>",
                error_text=str(err),
                function_name=make_archive.__name__,
            )
        )
        return ResponseData(
            error=f"{telegam_emogi.red_cross} Ошибка при создании архива",
            message=None,
        )
