import base64
from pathlib import Path

from aiohttp import ClientSession

from app.core.response import LoggingData, NetworkResponseData
from app.error_handlers.network import error_handler_for_the_website
from app.error_handlers.format import format_errors_message
from app.settings.response import messages


async def get_and_save_image(
    data_requests: str,
    path_img: Path,
    session: ClientSession,
    logging_data: LoggingData,
    base_64=False,
) -> NetworkResponseData:
    """
    Сохраняет data_requests по указанному если base_64 = True.

    Если data_requests это URL.Заходит по url, скачивает изображение
    и сохраняет его по указанному пути

    Args:
        data_requests (str): url для скачивания или строка в кодировке base64
        path_img (Path): Путь до картинки
        session (ClientSession): сессия для запроса
        logging_data (LoggingData): обьект класса LoggingData содержащий в себе логгер и имя роутера
        base_64 (Optional[bool], optional): Проверка на кодировку base_64. По умолачанию None

    Returns:
        NetworkResponseData: Объект с результатом запроса.

        Атрибуты NetworkResponseData:
            - message (Any | None): Путь до картинки (если запрос прошёл успешно).
            - error (str | None): Описание ошибки, если запрос завершился неудачей.
            - status (int): HTTP-код ответа. 0 — если ошибка возникла на клиентской стороне.
            - url (str): URL, по которому выполнялся запрос.
            - method (str): HTTP-метод, использованный при запросе.
    """
    try:
        if base_64:
            image_file: bytes = base64.b64decode(data_requests)

            path_img.parent.mkdir(parents=True, exist_ok=True)
            with open(path_img, "wb") as image:
                image.write(image_file)
        else:
            # Делаем запрос на сайт для получения данных о картинке
            response: NetworkResponseData = await error_handler_for_the_website(
                session=session,
                url=data_requests,
                logging_data=logging_data,
                data_type="BYTES",
                timeout=180,
                function_name=get_and_save_image.__name__,
            )
            if response.error:
                return response

            # Создаем папки если не существуют
            path_img.parent.mkdir(parents=True, exist_ok=True)
            with open(path_img, "wb") as file:
                file.write(response.message)

        return NetworkResponseData(
            message=path_img,
            url="<unknown>",
            method="GET",
            status=200,
        )
    except Exception as err:
        logging_data.error_logger.exception(
            format_errors_message(
                name_router=logging_data.router_name,
                method="GET",
                status=0,
                url="base64" if base64 else data_requests,
                error_text=str(err),
                function_name=get_and_save_image.__name__,
            )
        )
        return NetworkResponseData(
            error=messages.SERVER_ERROR,
            method="GET",
            status=0,
            url="base64" if base64 else data_requests,
        )
