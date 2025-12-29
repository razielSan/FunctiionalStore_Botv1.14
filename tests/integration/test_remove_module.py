from pathlib import Path
from typing import List

import pytest

from app.app_utils.module_creator.creator import create_module
from app.app_utils.module_remover.remover import remove_module
from app.app_utils.logging import setup_bot_logging, init_loggers
from app.core.response import ResponseData
from app.core.logging import LoggerStorage
from app.app_utils.filesistem import ensure_directories


@pytest.mark.integration
@pytest.mark.parametrize(
    "module",
    [
        "video",
        "audio/childes/main",
        "create/childes/data/childes/main/childes/audio/childes/create/childes/data",
    ],
)
def test_remove_module(tmp_path: Path, module):
    # tmp_path - временный путь для теста
    modules_root: Path = tmp_path / "test_app" / "bot" / "modules"
    log_path: Path = tmp_path / "logs" / "bot"
    temp_path: Path = tmp_path / "bot" / "temp"

    # Создаем директории
    log_path.mkdir(parents=True, exist_ok=True)
    tmp_path.mkdir(parents=True, exist_ok=True)
    modules_root.mkdir(parents=True, exist_ok=True)

    # создаем моудль
    resul: ResponseData = create_module(
        list_path_modules=[module],
        module_path=modules_root,
        root_package="test_app.bot.modules",
    )

    # Проверяем что модули создались
    assert resul.error is None
    assert resul.message == "module create"

    # Создаем temp папкy
    ensure_directories(temp_path / module)

    root_mod: str = module.split("/")[0]  # достаем корневой модуль для записи в лог
    init_loggers(
        bot_name="bot",
        setup_bot_logging=setup_bot_logging,
        log_format="[%(asctime)s] - %(module)s:%(lineno)s - [%(levelname)s - %(message)s]",
        date_format="%Y-%m-%D %H-%M-%S",
        base_path=tmp_path / "logs",
        list_router_name=[root_mod],
        log_data=LoggerStorage(),
    )

    # Проверяем что логгеры действительно созданы
    assert (log_path / root_mod / "error.log").exists()
    assert (log_path / root_mod / "info.log").exists()
    assert (log_path / root_mod / "warning.log").exists()

    remove_module(
        path_name=module,
        log_path=log_path,
        temp_path=temp_path,
        modules_path=modules_root,
        tests=True,
    )

    # Проверяем что модуль действительно удалился
    result_remove_module: bool = (modules_root / module).exists()
    assert result_remove_module is False

    # Проверяем что temp папка удалилась
    temp_remove: bool = (temp_path / module).exists()
    assert temp_remove is False

    # Если есть вложенные модули то достаем корневой
    base_module: List[str] = module.split("/")

    # Если корневой роутер то проверяем удалились ли логи
    if len(base_module) == 1:
        result_log_remove: bool = (log_path / base_module[0]).exists()
        result_log_remove is False

    if len(base_module) > 1:
        # Проверяем что корневой модуль не удалился
        result_remove_module: bool = (modules_root / base_module[0]).exists()
        assert result_remove_module is True

        # Проверяем что корневая папка temp для модуля не удалилась
        result_remove_temp: bool = (temp_path / base_module[0]).exists()
        assert result_remove_temp is True

        # Проверяем что корневые логи для модуля не удалились
        result_log_remove: bool = (log_path / base_module[0]).exists()
        assert result_log_remove is True
