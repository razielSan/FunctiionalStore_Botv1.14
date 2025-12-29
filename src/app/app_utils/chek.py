from app.core.response import ResponseData
from urllib.parse import urlparse


def checking_base64(data: str) -> bool:
    """
    Проверяет, являются ли входящие данные в формате base64.

    Args:
        data (str): Данные для проверки

    Returns:
        bool: True or False
    """
    if data.startswith("http"):
        return False
    return True


def chek_number_is_positivity(number: str) -> ResponseData:
    """
    Проверяет, является ли входящее  значение положительным числом.

    Args:
        number (str): Данные для проверки

    Returns:
        ResponseData: Возвращает экземпляр класса ResponseData

        Атрибуты ResponseData:
            - message (Any | None): Само число, если оно прошло проверку.
            - error (str | None): Описание ошибки, если число не прошло проверку.
    """

    try:
        number: int = int(number)
        if number <= 0:
            return ResponseData(error="⚠ Число должно быть больше 0")
        return ResponseData(message=number)
    except Exception:
        return ResponseData(error="⚠ Данные должны быть целым числом")


def is_valid_url(url: str) -> bool:
    """Проверяет url на валидность."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
