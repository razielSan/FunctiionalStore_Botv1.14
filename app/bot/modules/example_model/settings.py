from typing import Optional
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict, BaseSettings


# Пример 1
class Example(BaseModel):
    """Модель для примера 1."""

    SERVICE_NAME: str = "example"

    # Данные кнопок
    TEXT_PREFIX: str = "=)"
    CALLBACK_PREFIX: str = "example"

    API_KEY: Optional[str] = None


class ExampleModels(BaseSettings):
    """Модель для примера 1."""

    SERVICE_NAME: str = "example_model"

    MENU_REPLY_TEXT: str = "example_model"
    MENU_CALLBACK_TEXT: str = "example_model"
    MENU_CALLBACK_DATA: str = "example_model"
    NAME_FOR_TEMP_FOLDER: str = "example_model"

    PATH_TO_BOT_FOLDER: Path = Path(__file__).resolve().parent.parent.parent

    example: Example = Example()
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=PATH_TO_BOT_FOLDER / ".env",
        extra="ignore",
        env_nested_delimiter="__",
    )


# Пример 2
class ExampleMusic(BaseModel):
    """Модель для примера 2."""

    SERVICE_NAME: str = "example_Music"


class NewMusicItemsModels(BaseModel):
    """Модель для примера 2."""

    SERVICE_NAME: str = "new_music"

    # Данные кнопок для подлкючаемых моделей
    CALLBACK_BUTTON_TEXT_EXAMPLE_MUSIC: str = "1⃣ example_music"
    CALLBACK_BUTTON_DATA_EXAMPLE_MUSIC: str = "new_music example_music"

    example_music: ExampleMusic = ExampleMusic()


class MusicModels(BaseSettings):
    """Модель для примера 2."""

    SERVICE_NAME: str = "music"

    # Данные кнопок для подлключаемых моделей
    CALLBACK_BUTTON_TEXT_NEW_MUSIC: str = "🎻 Музыкальные новинки"
    CALLBACK_BUTTON_DATA_NEW_MUSIC: str = "music new_music"
    MENU_REPLY_TEXT: str = "🎧 Mузыка"

    new_music: NewMusicItemsModels = NewMusicItemsModels()


settings: ExampleModels = ExampleModels()
