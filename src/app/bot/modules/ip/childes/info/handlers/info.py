from typing import Union

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import pydantic_core
from app.bot.modules.ip.childes.info.settings import settings, NetworkConifg
from app.bot.modules.ip.childes.info.services.info import info_service
from app.bot.modules.ip.childes.info.api.info import info_api
from app.bot.modules.ip.childes.info.logging import get_log
from app.bot.core.paths import bot_path
from app.settings.response import messages
from app.app_utils.keyboards import get_reply_cancel_button
from app.core.response import ResponseData, NetworkResponseData

router: Router = Router(name=__name__)


class FSMInfoIP(StatesGroup):
    """FSM для модели info."""

    ip: State = State()
    spam: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def info(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    """Просит пользователя ввести ip для получения информации."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text="✏ Введите номер ip, о котором хотите узнать информацию в "
        "формате:\n\n"
        "192.168.0.3 -IPv4\n"
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - IPv6",
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMInfoIP.ip)


@router.message(FSMInfoIP.ip, F.text == messages.CANCEL_TEXT)
async def cancel_info_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отменяет все действия пользователя.

    Работа с FSMInfoIP.
    """
    await state.clear()
    await message.answer(text=messages.CANCEL_MESSAGE)
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )


@router.message(FSMInfoIP.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMInfoIP.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.message(FSMInfoIP.ip, F.text)
async def get_ip_information(
    message: Message,
    state: FSMContext,
    bot: Bot,
    session,
    get_main_keyboards,
):
    """
    Отправляет пользователю информацию по ip.

    Работа с FSMInfoIP.
    """

    chat_id = message.chat.id
    try:
        ip = NetworkConifg(any_ip=message.text)
    except pydantic_core._pydantic_core.ValidationError:
        await message.answer(f"⚠ {message.text} не соответствует формату IPv4 или IPv6")
        await bot.send_message(
            chat_id=chat_id,
            text="✏ Введите, снова, номер ip, о котором хотите узнать информацию в "
            "формате:\n\n"
            "192.168.0.3 - IPv4\n"
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334 - IPv6",
        )
        return
    ip: str = str(ip.any_ip)
    logging_data = get_log()
    ip_info: Union[ResponseData, NetworkResponseData] = await info_service.recieve(
        url=settings.ULR_IP_INFO.format(ip=ip, access_key=settings.ACCESS_KEY),
        path_folder_flag_country=bot_path.FLAG_DIR,
        path_folder_none_flag_img=bot_path.PATH_IMG_FLAG_NONE,
        session=session,
        logging_data=logging_data,
        info_api=info_api,
    )
    await state.clear()
    if ip_info.message:
        path_img: str = str(ip_info.message[0])
        data: str = ip_info.message[1]
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=FSInputFile(path=path_img),
            caption=data,
            reply_markup=ReplyKeyboardRemove(),
        )
        await message.answer(
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await message.answer(
            text=f"{ip_info.error}\n{messages.TRY_REPSONSE_MESSAGE}",
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
