from typing import Union

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiohttp import ClientSession

from app.bot.modules.find_image.childes.kinopoisk.settings import settings
from app.app_utils.keyboards import get_reply_cancel_button
from app.settings.response import messages
from app.bot.modules.find_image.childes.kinopoisk.services.kinopoisk import (
    kinopoisk_service,
)
from app.app_utils.filesistem import delete_data
from app.bot.modules.find_image.childes.kinopoisk.logging import get_log
from app.core.response import ResponseData, NetworkResponseData, LoggingData

router: Router = Router(name=__name__)


class FSMKinopoiskSearch(StatesGroup):
    """FSM для модели kinopoisk."""

    title: State = State()
    spam: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def kinopoisk(call: CallbackQuery, state: FSMContext) -> None:
    """
    Просит пользателя ввести названия фильмов.

    Работа с FSMKinopoiskSearch.
    """

    await state.set_state(FSMKinopoiskSearch.title)
    await call.message.answer(
        "✏ Введите названия фильмов через точку в "
        "формате\n\nматрица.криминальное чтиво.пражский студент",
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMKinopoiskSearch.title, F.text == messages.CANCEL_TEXT)
async def cancel_handler(
    message: Message, state: FSMContext, bot: Bot, get_main_keyboards
) -> None:
    """
    Отменяет все действия пользователя.

    Работа с FSMKinopoiskSearch.
    """

    await state.clear()
    await message.answer(
        text=messages.CANCEL_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )


@router.message(FSMKinopoiskSearch.spam, F.text)
async def get_message_is_state_spam(message: Message) -> None:
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMFindImageName.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.message(FSMKinopoiskSearch.title, F.text)
async def get_poster_kinopoisk(
    message: Message,
    state: FSMContext,
    session: ClientSession,
    bot: Bot,
    get_main_keyboards,
) -> None:
    """
    Отправляет пользователю архив с изображениями.

    Работа с FSMFindImageName.
    """

    # Встаем в состояние spam для отправки сообщения пользователю при запросе
    await state.set_state(FSMKinopoiskSearch.spam)

    # Получаем chat_id и логгеры
    chat_id: int = message.chat.id
    logging_data: LoggingData = get_log()

    # делаем запрос в service для получения архива
    archive_images: Union[
        ResponseData, NetworkResponseData
    ] = await kinopoisk_service.recieve(
        title=message.text,
        message=message,
        session=session,
        logging_data=logging_data,
    )
    archive = archive_images.message
    await state.clear()
    if archive:  # Если архив был создан
        await message.answer("⏳ Идет выгрузка архива в телеграм....")

        # Отправляем архив пользователю
        await bot.send_document(
            chat_id=chat_id,
            document=FSInputFile(path=archive),
            caption="Скаченные изображения",
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )

        delete_data(
            list_path=[archive],
            warning_logger=logging_data.warning_logger,
        )

    else:
        await message.answer(
            text=f"{archive_images.error}\n{messages.TRY_REPSONSE_MESSAGE}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
