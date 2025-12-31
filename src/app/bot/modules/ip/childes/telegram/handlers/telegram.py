from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.ip.childes.telegram.settings import settings
from app.bot.modules.ip.childes.telegram.api.telegram import telegram_api


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def kinopoisk(
    call: CallbackQuery,
) -> None:
    """Выводит информацию о API ID Telegram пользователя."""

    await call.message.edit_reply_markup(reply_markup=None)

    api_id_telegam = await telegram_api.get_user_info(
        api_id=call.message.chat.id,
        first_name=call.message.chat.first_name,
        user_name=call.message.chat.username,
        last_name=call.message.chat.last_name,
    )
    await call.message.answer(
        text=api_id_telegam.message,
        parse_mode="HTML",
    )
