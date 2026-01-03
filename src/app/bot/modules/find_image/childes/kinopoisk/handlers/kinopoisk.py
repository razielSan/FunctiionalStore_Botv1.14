from typing import Union, Dict
from pathlib import Path
import uuid
import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiohttp import ClientSession
from aiogram.exceptions import TelegramNetworkError

from app.bot.modules.find_image.childes.kinopoisk.settings import settings
from app.bot.modules.find_image.childes.kinopoisk.api.kinopoisk import kinopoisk_api
from app.app_utils.keyboards import get_reply_cancel_button
from app.settings.response import messages, telegam_emogi
from app.bot.modules.find_image.childes.kinopoisk.services.kinopoisk import (
    kinopoisk_service,
)
from app.app_utils.filesistem import save_delete_data
from app.bot.modules.find_image.childes.kinopoisk.logging import get_log
from app.core.response import ResponseData, NetworkResponseData, LoggingData
from app.core.paths import APP_DIR

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

    await call.message.edit_reply_markup(reply_markup=None)

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

    await message.answer(
        f"🔍 Ищу обложки по запросу: {message.text}...",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Получаем chat_id и логгеры
    chat_id: int = message.chat.id
    logging_data: LoggingData = get_log()

    path_image_folder: Path = (
        APP_DIR
        / "bot"
        / "temp"
        / settings.NAME_FOR_TEMP_FOLDER
        / str(message.from_user.id)
    )  # путь до временой папки хранения изображений

    # Путь до архива с картинками
    path_archive: Path = (
        APP_DIR / "bot" / "temp" / settings.NAME_FOR_TEMP_FOLDER / f"{uuid.uuid4().hex}"
    )
    # Формируем заголовок запроса
    HEADERS: Dict = settings.HEADERS.copy()
    HEADERS["X-API-KEY"] = settings.API_KEY

    progress_message: Message = await message.answer(
        text=f"📸 Загружено 0 из {len(message.text.split('.'))}"
    )  # сообщение для отслеживания прогресса скачивания

    # функция для отслеживания прогресса
    async def notify_progress(
        download: int = 0,
        count_images: int = 0,
        complete: bool = False,
    ):
        try:
            if not complete:
                await progress_message.edit_text(
                    text=f"📸 Загружено {download} из {count_images}",
                )
            else:
                await progress_message.edit_text(
                    f"✅ Готово! Загружено {download} изображений."
                )
        except Exception as err:
            print(err)

    # делаем запрос в service для получения архива
    archive_images: Union[
        ResponseData, NetworkResponseData
    ] = await kinopoisk_service.recieve(
        title=message.text,
        session=session,
        headers=HEADERS,
        path_archive=path_archive,
        path_image_folder=path_image_folder,
        logging_data=logging_data,
        notify_progress=notify_progress,
        url_search_video_name=settings.URL_SEARCH_VIDEO_NAME,
        kinopoisk_api=kinopoisk_api,
    )
    archive = archive_images.message
    await state.clear()
    if archive:  # Если архив был создан
        await message.answer("⏳ Идет выгрузка архива в телеграм....")

        try:
            retries: int = 3
            for _ in range(retries):  # безопасно отправляем архив пользователю
                try:
                    await bot.send_document(
                        chat_id=chat_id,
                        document=FSInputFile(path=archive),
                        caption="🌆 Скачанные изображения",
                        reply_markup=ReplyKeyboardRemove(),
                        request_timeout=180,
                    )
                    break
                except PermissionError:
                    await asyncio.sleep(1)
        except TelegramNetworkError:
            logging_data.info_logger.exception(
                msg="Telegram timeout while uploading archive"
            )
            await bot.send_message(
                chat_id=chat_id,
                text=f"{telegam_emogi.red_cross} Произошла ошибка при загрузке архива в телеграм...",
            )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )

        await save_delete_data(
            list_path=[archive],
            warning_logger=logging_data.warning_logger,
        )  # удаляем архив

    else:
        await message.answer(
            text=f"{archive_images.error}\n{messages.TRY_REPSONSE_MESSAGE}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
