import aiohttp

from bot.core.startup import setup_bot
from bot.core.bot import telegram_bot
from bot.core.config import bot_error_logger, bot_info_logger


async def run_bot() -> None:
    """Подлючает все параметры для бота и запускает его."""
    # Встаем в try/except чтобы отловить все что не попало в middleware
    try:

        main_keyboards, dp = await setup_bot()

        # Создаем глобальную сессию для всего бота. Будет доступ в роутерах через
        # название указанное ниже
        async with aiohttp.ClientSession() as session:
            dp["session"] = session
            dp["main_keyboards"] = main_keyboards
            bot_info_logger.info("bot запущен")
            await dp.start_polling(telegram_bot)

    except Exception as err:
        bot_error_logger.exception(f"Критическая ошибка при работа бота bot: {err}")
