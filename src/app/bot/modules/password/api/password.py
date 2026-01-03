from typing import List, Union
import random

from app.bot.modules.password.settings import settings
from app.core.response import ResponseData


class PasswordAPI:
    async def get_generateing_simple_or_difficult_password(
        self,
        password_hard: str,
        step: str = 3,
        count_password: int = 20,
    ) -> ResponseData:
        """
        Генерирует сложный или простой пароль

        Args:
            password_hard (str): Тип сложности пароля
            step (str, optional): Шаг пароля[По умолчанию 3]. Допустимые варианты 1-4
            count_password (int): Количество паролей. По умолчанию 15

        Returns:
            ResponseData: Объект с результатом запроса.

            Атрибуты ResponseData:
                - message (Any | None): Данные успешного ответа (если запрос прошёл успешно).
                - error (str | None): Описание ошибки, если запрос завершился неудачей.
        """
        array_generating_password: List = []

        def random_generate_value(
            generation_data: str,
            step: int,
        ) -> str:
            """

            Формирует строку содержащую колиечство шагов(step) состоящую либо из букв
            либи из цифр

            Args:
                generation_data (Union[str, List]): Данные из которых будет генерироваться выборка
                step (int): Количество шагов пароля

            Returns:
                str: Возвращает строки содержащую или буквы или фифры
            """

            # Т.к в generation data может быть список выбираем рандомное значение из списка
            # если не список а строка выбираем ее
            values: str = (
                random.choice(generation_data)
                if isinstance(generation_data, list)
                else generation_data
            )

            # Определяем рандомное значение флага, если True то берем рандомное значение из
            # деneration data и следущие за ним цифры с учетом шага, если Fals то берем
            # рандомное значение genaration data и умножаем на шаг
            current_flag: bool = random.choice([True, False])
            if current_flag:
                start: int = random.randrange(0, len(generation_data) - step + 1)

                values = values[start : start + step]

                # Если False то берем значение в обратном порядке
                current_flag = random.choice([True, False])
                if current_flag:
                    values = values[::-1]

            else:
                values = random.choice(values) * step

            return values

        # Определяем сложноый или простой нужен пароль
        count: int = 7 if password_hard == settings.DIFFICULT else 4

        for _ in range(1, count_password + 1):  # Определяем количество паролей
            password: str = ""

            for i in range(1, count):  # Определяем количество символов в пароле

                # Определяем что будет добавляться буквы или цифвры
                generation_data: Union[str, List] = (
                    settings.DIGITS if i % 2 == 0 else settings.KEYBOARD_LAYOUT_ENGLISH
                )
                result_password: str = random_generate_value(
                    generation_data=generation_data,
                    step=step,
                )

                password += result_password

            array_generating_password.append(password)
        # Формируем строку с паролями
        passwords: str = "\n".join(array_generating_password)
        return ResponseData(
            message=passwords,
            status=200,
        )


password_api: PasswordAPI = PasswordAPI()
