from pydantic import BaseModel


class FeatureSettings(BaseModel):
    """Модель для главного меню."""

    SERVICE_NAME: str = "example_model.features"

    MENU_REPLY_TEXT: str = "example_model.features"
    MENU_CALLBACK_TEXT: str = "example_model.features"
    MENU_CALLBACK_DATA: str = "example_model.features"
    NAME_FOR_TEMP_FOLDER: str = "example_model.features"


settings: FeatureSettings = FeatureSettings()
