import shutil
from pathlib import Path


def remove_module(
    path_name: str,
    log_path: Path,
    temp_path: Path,
    modules_path: Path,
    tests=False,
):
    """
    Удаляет модуль и его дочерние модули, temp папку связаную с модулями и log модуля если родительский.

    Args:
        path_name (str): Путь от папки с модулем до удаляемого модуля

        Пример:
        video/childes/name

        log_path (Path): путь до папки с логами
        temp_path (Path): путь до temp папки
        modules_path (Path): путь до папки с модулями
    """
    modules_path = modules_path / path_name

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

    # 2. Удлаляем temp папки
    temp_folder = temp_path / path_name
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
        print(f"Удалена папка {temp_folder} и ее дочерние папки")
    # 3. Удлаляем логи
    log_path = log_path / path_name
    if log_path.exists():
        shutil.rmtree(log_path)
        print(f"Удалены логи - {log_path}")

    print(f"Процедура удаления {path_name} завершена")
