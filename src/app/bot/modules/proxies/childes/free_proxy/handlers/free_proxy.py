from typing import Union

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


from app.bot.modules.proxies.childes.free_proxy.settings import settings
from app.bot.modules.proxies.childes.free_proxy.logging import get_log
from app.bot.modules.proxies.childes.free_proxy.extension import get_free_proxy
from app.bot.modules.proxies.childes.free_proxy.keyboards.inline import (
    get_free_proxy_keyboards_inline_kb,
)
from app.bot.modules.proxies.childes.free_proxy.services.free_proxy import (
    free_proxy_service,
)
from app.settings.response import messages
from app.core.response import NetworkResponseData, ResponseData


router: Router = Router(name=__name__)


class FSMFreeProxy(StatesGroup):
    """FSM для модели free_proxy"""

    spam: State() = State()


@router.message(FSMFreeProxy.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работса с FSMFreeProxy.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(
    StateFilter(None),
    F.data == settings.MENU_CALLBACK_DATA,
)
async def free_proxy(call: CallbackQuery):
    """Отправляет пользователю клавиатуру с вариантами выбора типа прокси."""

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_free_proxy_keyboards_inline_kb,
    )


@router.callback_query(F.data.startswith(settings.CALLBACK_PREFIX))
async def get_data_proxies(
    call: CallbackQuery, state: FSMContext, bot: Bot, get_main_keyboards
):
    """
    Возвращает пользователю работающие прокси.

    Работса с FSMFreeProxy.
    """

    chat_id: int = call.message.chat.id

    # Встаем в состояние spam для овтета пользователю во время запроса
    await state.set_state(FSMFreeProxy.spam)

    # Удаляем инлайн клавиатуру
    await call.message.edit_reply_markup(reply_markup=None)

    await bot.send_message(
        chat_id=call.message.chat.id,
        text=messages.START_RESPONSE,
        reply_markup=ReplyKeyboardRemove(),
    )

    # получаем тип прокси для запроса
    type_proxy: str = call.data.split(" ")[1]

    progress_message = await call.message.answer(messages.WAIT_MESSAGE)

    async def notifier(text: str):
        try:
            await progress_message.edit_text(text)
        except Exception:
            pass

    logging_data = get_log()

    free_proxy: Union[
        ResponseData, NetworkResponseData
    ] = await free_proxy_service.recieve(
        type_proxy=type_proxy,
        list_data_proxies=settings.LIST_DATA_PROXIES,
        get_free_proxy=get_free_proxy,
        notify_progress=notifier,
        logging_data=logging_data,
    )

    await state.clear()
    if free_proxy.message:
        await bot.send_message(chat_id=chat_id, text=free_proxy.message)
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=f"{free_proxy.error}\n{messages.TRY_REPSONSE_MESSAGE}",
            reply_markup=get_main_keyboards,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.OPTIONS_BOT_MESSAGE,
            reply_markup=get_free_proxy_keyboards_inline_kb,
        )
