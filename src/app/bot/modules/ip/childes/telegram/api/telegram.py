from typing import Optional

from aiogram.utils.markdown import hbold
from app.core.response import ResponseData


class TeleramAPI:
    async def get_user_info(
        self,
        api_id: int,
        first_name: str,
        user_name: str,
        last_name: Optional[str],
    ) -> ResponseData:
        """

        Функция для получения информации о пользователе

        Args:
            api_id (int): Id telegram пользователя
            first_name (str): Имя пользователя
            user_name (str): Логин пользователя
            last_name (Optional[str]): Фамилия пользователя[По умолчанию None]

        Returns:
            str: Строка содержащая информацию о пользователе по api id telegram
        """
        # Формируем сообщение о пользователе
        user_str: str = (
            f"@{user_name}\nId: {hbold(api_id)}\nFirst name: {hbold(first_name)}\n"
            f"Last_name: {hbold(last_name)}\n"
        )

        return ResponseData(message=user_str)


telegram_api: TeleramAPI = TeleramAPI()
