from pathlib import Path
from typing import List

import pytest

from app.app_utils.module_creator.creator import create_module
from app.app_utils.module_remover.remover import remove_module
from app.core.response import ResponseData
from app.app_utils.filesistem import ensure_directories


@pytest.mark.parametrize(
    "modules",
    [
        ["video"],
        ["audio/childes/main"],
        ["create/childes/data/childes/main/childes/audio/childes/create/childes/data"],
    ],
)
def test_remove_module(tmp_path: Path, modules):
    # tmp_path - временный путь для теста
    modules_root: Path = tmp_path / "test_app" / "bot" / "modules"
    log_path: Path = tmp_path / "logs" / "bot"
    temp_path: Path = tmp_path / "bot" / "temp"

    # Создаем директории
    log_path.mkdir(parents=True, exist_ok=True)
    tmp_path.mkdir(parents=True, exist_ok=True)
    modules_root.mkdir(parents=True, exist_ok=True)

    resul: ResponseData = create_module(
        list_path_modules=modules,
        module_path=modules_root,
        root_package="test_app.bot.modules",
    )

    # Проверяем что модули создались
    assert resul.error is None
    assert resul.message == "module create"

    # Создаем temp папки
    for tmp in modules:
        ensure_directories(temp_path / tmp)

    for module in modules:
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
        if len(base_module) > 1:
            # Проверяем что корневой модуль не удалился
            result_remove_module: bool = (modules_root / base_module[0]).exists()
            assert result_remove_module is True

            # Проверяем что корневая папка temp для модуля не удалилась
            result_remove_temp: bool = (temp_path / base_module[0]).exists()
            assert result_remove_temp is True
