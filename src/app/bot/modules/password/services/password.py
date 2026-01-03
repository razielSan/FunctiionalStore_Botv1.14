from app.error_handlers.decorator import safe_async_execution
from app.bot.modules.password.api.password import password_api

from app.core.response import LoggingData, ResponseData


class PasswordService:
    async def recieve(
        self,
        type_password: str,
        logging_data: LoggingData,
        step: int = 3,
        count_password: int = 20,
    ) -> ResponseData:
        """
        Application service для сценария генерации паролей.

        Отвечает за:
        - взаимодействие с PasswordAPI
        - отлавливание ошибок
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        decorator_function = safe_async_execution(
            logging_data=logging_data,
        )
        func = decorator_function(
            password_api.get_generateing_simple_or_difficult_password,
        )

        result_password: ResponseData = await func(
            password_hard=type_password,
            step=step,
            count_password=count_password,
        )
        return result_password


password_service: PasswordService = PasswordService()
