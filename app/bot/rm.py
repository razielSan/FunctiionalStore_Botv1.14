import shutil
from pathlib import Path


LOG_PATH = Path("logs/bot")
TEMP_PATH = Path("bot/temp")
MODULES_PATH = Path("bot/modules")


def remove_module(name: str):
    modules_path = MODULES_PATH / name

    if not modules_path.exists():
        print(f"Модуль {name} не найден")
        return

    # 1. Удаляем модуль
    shutil.rmtree(modules_path)
    print(f"Папка модуля удалена: {modules_path}")

    # Удлаляем temp папки
    temp_folder_name = name.replace("/", ".")
    temp_folder = TEMP_PATH / temp_folder_name
    for temp_name in TEMP_PATH.iterdir():
        print(temp_name)
        print(temp_folder)
        if str(temp_name).startswith(f"{str(temp_folder)}."):
            shutil.rmtree(temp_name)
            print(f"Удалена childe temp папка {temp_name}")

    if temp_folder.exists():
        shutil.rmtree(temp_folder)
        print(f"Удалена root temp папка {temp_folder}")

    # Удаляем логи
    log_folder_name = name.split("/")[0]
    log_folder = LOG_PATH / log_folder_name
    print(log_folder)
    if log_folder.exists():
        shutil.rmtree(log_folder)
        print(f"Удалены логи {log_folder_name}")

    print("Модуль успешно удален")


if __name__ == "__main__":
    import sys

    # if len(sys.argv)
    print(len(sys.argv))
    remove_module(sys.argv[1])

# python bot/rm.py video/main/audio
