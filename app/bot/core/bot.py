from aiogram import Bot, Dispatcher
from bot.core.config import bot_settings

telegram_bot: Bot = Bot(token=bot_settings.TOKEN)
dp: Dispatcher = Dispatcher()
