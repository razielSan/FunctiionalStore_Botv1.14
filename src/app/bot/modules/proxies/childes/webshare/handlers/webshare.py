from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
import aiohttp

from app.bot.modules.proxies.childes.webshare.settings import settings
from app.bot.modules.proxies.childes.webshare.services.webshare import webshare_service
from app.settings.response import messages


router = Router(name=__name__)


class FSMWebshare(StatesGroup):
    spam: State = State()


@router.message(FSMWebshare.spam, F.text)
async def get_message_is_state_spam(message: Message):
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def webshare(
    call: CallbackQuery,
    state: FSMContext,
    session: aiohttp.ClientSession,
    bot: Bot,
    get_main_keyboards,
):

    await state.set_state(FSMWebshare.spam)
    await state.update_data(spam=True)

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    # Получаем прокси
    proxies_data = await webshare_service.receive(session=session)
    await state.clear()
    if proxies_data.message:
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=proxies_data.message,
        )
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await bot.send_message(
            chat_id=call.message.chat.id,
            text=f"{proxies_data.error}\n{messages.TRY_REPSONSE_MESSAGE}",
            reply_markup=get_main_keyboards,
        )
