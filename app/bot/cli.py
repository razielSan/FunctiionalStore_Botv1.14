import argparse
from pathlib import Path

from app_utils.modules import create_module


def creates_new_modules_via_the_command_line() -> None:
    """
    Создает новые модули для бота через командную строку.

    python -m bot.cli video video/create audio
    """
    parser = argparse.ArgumentParser(description="Create new bot modules.")
    parser.add_argument("modules_names", type=str, nargs="+", help="Modules names")
    args = parser.parse_args()
    rel_path_to_modules: Path = Path("bot") / Path("modules")
    create_module(
        list_name_modules=args.modules_names,
        rel_path_to_modules=rel_path_to_modules,
    )

    print(f"Modules {', '.join(args.modules_names)} created successfully")


if __name__ == "__main__":
    creates_new_modules_via_the_command_line()
