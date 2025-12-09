import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
import aiohttp

from settings.response import messages
from error_handlers.decorator import safe_async_execution
from bot.modules.proxies.mod_webshare.settings import settings
from bot.modules.proxies.mod_webshare.utils.webshare import get_proxies_by_webshare
from bot.modules.proxies.mod_webshare.logging import get_log


router: Router = Router(name="proxies.mod_webshare")


class FSMWebshare(StatesGroup):
    spam: State = State()


@router.message(FSMWebshare.spam, F.text)
async def get_message_when_requested(message: Message, state: FSMContext):
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

    proxies_logging_data = get_log()

    # Отлавливаем все возмоэжные ошибки
    decorator_function = safe_async_execution(
        logging_data=proxies_logging_data,
    )
    func = decorator_function(get_proxies_by_webshare)

    # Получаем прокси
    proxies_data = await func(
        api_key=settings.ApiKey,
        url_config=settings.URL_CONFIG,
        url_proxeis_list=settings.URL_PROXIES_LIST,
        session=session,
        logging_data=proxies_logging_data,
    )
    if proxies_data.message:
        await state.clear()
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
