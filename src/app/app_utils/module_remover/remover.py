import shutil
from pathlib import Path
import logging


def remove_module(
    path_name: str,
    log_path: Path,
    temp_path: Path,
    modules_path: Path,
    close_loggers: bool = True,
    tests: bool = False,
):
    """
    Удаляет модуль и его дочерние модули, temp папку связанную с модулями и log модуля если родительский.

    Args:
        path_name (str): Путь от папки с модулем до удаляемого модуля

        Пример:
        video/childes/name

        log_path (Path): путь до папки с логами
        temp_path (Path): путь до temp папки
        modules_path (Path): путь до папки с модулями
        close_loggers (bool): флаг для закрытия логгеров.По умолчанию True
        tests (bool): флаг для проверки функции в тестах
    """

    # Закрываем логи, если есть открытые
    if close_loggers:
        logging.shutdown()

    modules_path: Path = modules_path / path_name

    if not modules_path.exists():
        print(f"Модуль {path_name} не найден")
        return

    result = None
    if not tests:
        result = input(
            f"Вы точно хотите удалить модуль - {path_name}\n1. "
            "Да - Нажмите 'Enter'\n2. Нет - Отправьте любой символ"
        )

    # 1. Удаляем модуль
    if not result:
        shutil.rmtree(modules_path)
        print(f"Модуль {path_name} " "и его дочерние модули успешно удалены")
    else:
        print(f"Удаление модуля {path_name} отменено")
        return

    # 2. Удаляем temp папки
    temp_folder: Path = temp_path / path_name
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
        print(f"Удалена папка {temp_folder} и ее дочерние папки")
    # 3. Улаляем логи
    log_path: Path = log_path / path_name
    if log_path.exists():
        shutil.rmtree(log_path)
        print(f"Удалены логи - {log_path}")

    print(f"Процедура удаления {path_name} завершена")
