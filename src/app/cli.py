from typing import List
from pathlib import Path
import sys

from app.scripts.bot.create_module import creates_new_modules_via_the_command_line
from app.scripts.bot.remove_module import remove_module
from app.core.paths import APP_DIR


MODULES_ROOT: Path = APP_DIR / "bot" / "modules"


def main() -> None:
    """
    Команды для командной строки.

    cli add-module <путь> <путь> - Создание модулей
    cli remove-module <путь> - Удаление модуля
    """

    list_sys_argv: List[str] = sys.argv

    if len(list_sys_argv) < 2:
        print(
            "Использование:\n\npython manage.py add-module <путь>\npython manage.py remove-module <путь>"
        )
        sys.exit()

    command: str = list_sys_argv[1]
    if command == "add-module":
        if len(list_sys_argv) < 3:
            print(
                "Укажите путь до модуля.Дочерний модуль должен быть "
                "разделен 'childes'\ncli add-module <путь>"
                "\ncli add-module test/childes/data"
            )
            exit()
        else:
            print("Идет создание модулей...")
            creates_new_modules_via_the_command_line(
                list_path_modules=list_sys_argv[2:],
                module_path=MODULES_ROOT,
                root_package="app.bot.modules",
            )
    elif command == "remove-module":
        if len(list_sys_argv) < 3:
            print(
                "Укажите путь до модуля.Дочерний модуль должен быть "
                "разделен 'childes'\ncli add-module <путь>"
                "\ncli add-module test/childes/data"
            )
            exit()
        elif len(list_sys_argv) >= 4:
            print(
                "За раз можно удалить только один модуль\ncli remove-module <путь>"
            )
            exit()
        else:
            LOG_PATH: Path = APP_DIR / "logs" / "bot"
            TEMP_PATH: Path = APP_DIR / "bot" / "temp"
            MODULES_PATH: Path = MODULES_ROOT
            remove_module(
                path_name=list_sys_argv[2],
                log_path=LOG_PATH,
                temp_path=TEMP_PATH,
                modules_path=MODULES_PATH,
            )
    elif command == "help":
        print(
            """Доступные команды:
              
cli add-module <путь> <путь> - Создание модулей
cli remove-module <путь> - Удаление модуля 
"""
        )
    else:
        print("Неизвестная команда\n\npython manage.py help - Основные команды")
