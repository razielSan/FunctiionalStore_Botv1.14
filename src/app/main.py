import asyncio
import signal
import sys

from app.bot.main import run_bot
from app.bot.core.bot import telegram_bot
from app.settings.init_logging import root_warning_logger, root_info_logger

# Меняет тип event_loop для виндоус чтобы при нажатии ctl+c не было ошибки KeyboardInterrupt
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def main() -> None:
    """Синхронная точка входа для console_scripts."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        root_info_logger.info("Приложение остановлено вручную (Ctrl+C)")


async def async_main() -> None:
    """Async логика приложения."""
    if sys.platform == "win32":
        await _run_windows()
    else:
        await _run_unix()


async def _run_unix():
    """Запуск приложения на unix-системе."""
    # корректно завершает работу на сервере
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    root_info_logger.info("Приложение запущен(Unix mode)")
    await asyncio.gather(run_bot(), stop_event.wait())


async def _run_windows():
    """Запуск приложения на windows."""
    try:
        # Запускам бота
        root_info_logger.info("Приложение запущено (Windows mode)")
        await run_bot()
    except Exception:
        pass
    finally:
        # Завершаем работy для windows
        root_info_logger.info("Приложение завершает работу")
        try:
            if getattr(telegram_bot, "session", None):
                await telegram_bot.session.close()  # аккуратно закрываем сессию
        except RuntimeError:
            root_warning_logger.warning(
                "Сессия уже была закрыта или event loop завершен"
            )
        except Exception as err:
            root_warning_logger.warning(f"Ошибка при закрытии сессии: {err}")
        root_info_logger.info("Приложение завершило работу корректно")


# async def main() -> None:
#     """Запуск основного приложения."""
#     # Если платформа ни виндоус
#     if sys.platform != "win32":
#         # корректно завершает работу на сервере
#         loop = asyncio.get_event_loop()
#         stop_event = asyncio.Event()

#         for sig in (signal.SIGINT, signal.SIGTERM):
#             loop.add_signal_handler(sig, stop_event.set)

#         root_info_logger.info("Приложение запущен(Unix mode)")
#         await asyncio.gather(run_bot(), stop_event.wait())
#     else:
#         try:
#             # Запускам бота
#             root_info_logger.info("Приложение запущено (Windows mode)")
#             await run_bot()
#         except Exception:
#             pass
#         finally:
#             # Завершаем работy для windows
#             root_info_logger.info("Приложение завершает работу")
#             try:
#                 if getattr(telegram_bot, "session", None):
#                     await telegram_bot.session.close()  # аккуратно закрываем сессию
#             except RuntimeError:
#                 root_warning_logger.warning(
#                     "Сессия уже была закрыта или event loop завершен"
#                 )
#             except Exception as err:
#                 root_warning_logger.warning(f"Ошибка при закрытии сессии: {err}")
#             root_info_logger.info("Приложение завершило работу корректно")


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:  # Проглатываем ошибку KeyboardInterrupt для windows чтобы не отображалась
#         root_info_logger.info("Приложение остановлено вручную (Ctrl+C)")
