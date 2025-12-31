from pathlib import Path

import pytest

from app.app_utils.module_creator.creator import create_module
from app.core.response import ResponseData


@pytest.mark.unit
@pytest.mark.parametrize(
    "modules",
    [
        ["video"],
        ["video/childes/main"],
        ["video/childes/data/childes/main/childes/audio/childes/create/childes/data"],
        ["video/childes/video/childes/video"],
        ["audio/childes/test", "audio/childes/test"],
        [
            "audio/childes/test",
            "video/childes/test",
            "data/childes/test",
            "create/childes/test",
        ],
    ],
)
def test_create_module(tmp_path: Path, modules):
    # tmp_path - временный путь для теста
    modules_root: Path = tmp_path / "test_app" / "bot" / "modules"
    modules_root.mkdir(parents=True, exist_ok=True)

    resul: ResponseData = create_module(
        list_path_modules=modules,
        module_path=modules_root,
        root_package="test_app.bot.modules",
    )

    assert resul.error is None
    assert resul.message == "module create"

    # Проверяем что модули действительно созданы
    for module_name in modules:
        module_path = modules_root / module_name
        assert module_path.exists()
        assert module_path.is_dir()

        # Основные файлы  должны существовать
        for filename in ["router.py", "settings.py", "logging.py", "response.py"]:
            assert (module_path / filename).exists()

        # Основные директории
        for dirname in [
            "childes",
            "fsm",
            "services",
            "utils",
            "handlers",
            "keyboards",
            "api",
        ]:
            assert (module_path / dirname).exists()
            assert ((module_path / dirname) / "__init__.py").exists()

        # Проверяем что в router.py имя подставленно корректно
        router_file = module_path / "router.py"
        content = router_file.read_text(encoding="utf-8")
        module_name_formatted = module_name.replace("/", ".")
        assert f"Router(name='{module_name_formatted}')" in content


@pytest.mark.unit
@pytest.mark.parametrize(
    "modules",
    [
        ["video/childes", "video"],
        ["video/wrong/childes"],
        ["video/./data"],
        ["video//data"],
        ["audio/childes/video", "audio/childes/video/./create"],
        ["audio/childes/test/childes/test/childe/test"],
    ],
)
def test_create_module_invalid_childes(tmp_path: Path, modules):
    # tmp_path - временный путь для теста
    modules_root: Path = tmp_path / "test_app" / "bot" / "modules"
    modules_root.mkdir(parents=True)

    result: ResponseData = create_module(
        list_path_modules=modules,
        module_path=modules_root,
        root_package="test_app.bot.modules",
    )

    assert result.error is not None
    assert isinstance(result.error, str)
