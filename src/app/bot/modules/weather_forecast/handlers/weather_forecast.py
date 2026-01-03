from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from app.bot.modules.weather_forecast.settings import settings
from app.bot.modules.weather_forecast.response import get_keyboards_menu_buttons
from app.settings.response import messages


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == settings.MENU_REPLY_TEXT)
async def weather_forecast(message: Message, bot: Bot) -> None:
    """
    Главный обработчик для модуля weather_forecast..

    Возвращает инлайн клавиатуру с вариантами выбора.
    """
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass
    await message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_keyboards_menu_buttons,
    )
