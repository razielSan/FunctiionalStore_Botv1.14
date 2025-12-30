from typing import Callable, Optional, Union, Any
from asyncio import AbstractEventLoop, exceptions
import functools
import traceback
from logging import Logger
import importlib
from types import ModuleType

from app.core.response import LoggingData, ResponseData
from app.error_handlers.format import format_errors_message
from app.settings.response import messages


async def run_safe_inf_executror(
    loop: AbstractEventLoop,
    func: Callable,
    *args,
    logging_data: Optional[LoggingData] = None,
    **kwargs,
) -> Union[Any, ResponseData]:
    """
    Отлавливает все возможные ошибки для переданной синхронной функции.

    При ошибке в ходе выполнения функции выкидывает обьект класса ResponseData

    Args:
        loop (AbstractEventLoop): цикл событий
        func (Callable): функция для цикла
        logging_data (Optional[LoggingData], optional): обьект класс
        LoggingData содержащий логгер и имя роутера. None по умолчанию

    Returns:
        Union[Any, NetworkResponseData]: Возвращает loop.run_in_executor
    """
    try:
        return await loop.run_in_executor(
            None,
            functools.partial(
                func,
                *args,
                **kwargs,
            ),
        )
    except exceptions.CancelledError:
        print("Остановка работы процесса пользователем")
        return ResponseData(
            message="Остановка работы процесса пользователем",
            error=None,
        )

    except Exception as err:
        if logging_data:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    status=0,
                    method="<unknown>",
                    url="<unknown>",
                    error_text=err,
                    function_name=func.__name__,
                )
            )
        else:
            print(err)
        return ResponseData(
            error=messages.SERVER_ERROR,
            message=None,
        )


def safe_import(
    module_path: str,
    error_logger: Logger = None,
) -> Optional[ModuleType]:
    """
    Безопасный импорт модуля.

    Возвращает модуль или None если произошла ошибка.
    """
    try:
        return importlib.import_module(module_path)
    except Exception as err:
        if error_logger:
            error_logger.error(
                f"[AUTO IMPORT ERROR] Модуль {module_path} не загрузился\n"
                f"{err}\n{traceback.format_exc()}"
            )
        else:
            print(
                f"[AUTO IMPORT ERROR] Модуль {module_path} не загрузился\n"
                f"{err}\n{traceback.format_exc()}"
            )
        return None
