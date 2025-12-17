from aiogram import Bot, Dispatcher
from app.bot.core.init_logging import bot_settings

telegram_bot: Bot = Bot(token=bot_settings.TOKEN)
dp: Dispatcher = Dispatcher()
