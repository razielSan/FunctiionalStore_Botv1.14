import sys
from pathlib import Path
from typing import List

from aiogram import Dispatcher
import pytest

from app.app_utils.module_creator.creator import create_module
from app.app_utils.module_loader.loader import (
    load_modules,
    get_child_modules_settings_inline_data,
    get_child_modules_settings_temp_folder,
)
from app.settings.init_logging import root_error_logger
from app.core.modules_loader import ModuleInfo
from app.core.response import ResponseData


@pytest.mark.integration
def test_load_modules_integration(tmp_path: Path):
    # Создаем структуру
    modules_path: Path = tmp_path / "test_app" / "bot" / "modules"
    modules_path.mkdir(parents=True)
    modules: List[str] = [
        "video/childes/audio",
        "video/childes/temp",
        "video/childes/data",
        "video/childes/create",
        "video/childes/create/childes/temp",
        "video/childes/create/childes/data",
        "video/childes/create/childes/name",
        "video/childes/create/childes/name/childes/test",
        "test",
        "audio/childes/create",
        "create/childes/data",
    ]

    result: ResponseData = create_module(
        list_path_modules=modules,
        module_path=modules_path,
        root_package="test_app.bot.modules",
    )

    assert result.error is None
    dp: Dispatcher = Dispatcher()
    try:
        sys.path.insert(0, str(tmp_path))

        list_modules = load_modules(
            dp=dp,
            error_logger=root_error_logger,
            modules_path=Path(
                modules_path,
            ),
            root_package="test_app.bot.modules",
        )
        assert len(list_modules) == 14

        for module in list_modules:
            assert isinstance(module, ModuleInfo)
            assert module.router is not None
            assert module.settings is not None

        # Тестируем на возможных вариантах функции get_child_modules_settings_inline_data
        array_video = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("video/childes"),
            root_package="test_app.bot.modules.video.childes",
            error_logger=root_error_logger,
        )
        assert len(array_video) == 4

        array_video_create = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("video/childes/create/childes"),
            root_package="test_app.bot.modules.video.childes.create.childes",
            error_logger=root_error_logger,
        )
        assert len(array_video_create) == 3

        array_video_create_name = get_child_modules_settings_inline_data(
            module_path=modules_path
            / Path("video/childes/create/childes/name/childes"),
            root_package="test_app.bot.modules.video.childes.create.childes.name.childes",
            error_logger=root_error_logger,
        )
        assert len(array_video_create_name) == 1

        array_test = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("test/childes"),
            root_package="test_app.bot.modules.test.childes",
            error_logger=root_error_logger,
        )
        assert len(array_test) == 0

        array_audio = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("audio/childes"),
            root_package="test_app.bot.modules.audio.childes",
            error_logger=root_error_logger,
        )
        assert len(array_audio) == 1

        array_audio_create = get_child_modules_settings_inline_data(
            module_path=modules_path / Path("audio/childes/create/childes"),
            root_package="test_app.bot.modules.audio.childes.create.childes",
            error_logger=root_error_logger,
        )
        assert len(array_audio_create) == 0

        # Тестирование функции get_child_modules_settings_temp_folder
        array_temp_folder = get_child_modules_settings_temp_folder(
            module_path=modules_path,
            error_logger=root_error_logger,
            root_package="test_app.bot.modules",
        )
        assert len(array_temp_folder) == 14

    finally:
        sys.path.remove(str(tmp_path))
