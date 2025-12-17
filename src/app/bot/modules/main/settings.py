from pydantic import BaseModel


class MainRouterSettings(BaseModel):
    """Модель для главного меню."""

    SERVICE_NAME: str = "main"
    MENU_REPLY_TEXT: str = "main"
    MENU_CALLBACK_TEXT: str = "main"
    MENU_CALLBACK_DATA: str = "main"
    NAME_FOR_TEMP_FOLDER: str = "main" 


settings: MainRouterSettings = MainRouterSettings()
