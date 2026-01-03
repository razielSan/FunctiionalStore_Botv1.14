from typing import Dict, Union
from pathlib import Path
import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramNetworkError

from app.bot.modules.find_image.childes.find_name_image.settings import settings
from app.bot.modules.find_image.childes.find_name_image.adapters import (
    get_images_adapter,
)
from app.bot.modules.find_image.childes.find_name_image.extensions import (
    Crawler,
    Google,
)
from app.bot.modules.find_image.childes.find_name_image.services.find_name_image import (
    find_name_image_service,
)
from app.bot.modules.find_image.childes.find_name_image.logging import get_log
from app.settings.response import messages, telegam_emogi
from app.app_utils.keyboards import get_reply_cancel_button
from app.app_utils.chek import chek_number_is_positivity
from app.app_utils.filesistem import save_delete_data
from app.core.paths import APP_DIR
from app.core.response import ResponseData, NetworkResponseData


router: Router = Router(name=__name__)


class FSMFindImageIcrawler(StatesGroup):
    """FSM для модели find_name_image (service icrawler)."""

    title: State = State()
    count: State = State()
    spam: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def find_image_name(call: CallbackQuery, state: FSMContext) -> None:
    """
    Просит пользователя ввести название изображения.

    Работа с FSMFindImageName.
    """

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text="🧑‍💻  Введите название изображения",
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMFindImageIcrawler.title)


@router.message(FSMFindImageIcrawler.title, F.text == messages.CANCEL_TEXT)
@router.message(FSMFindImageIcrawler.count, F.text == messages.CANCEL_TEXT)
async def cancel_find_image_name_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отменяет все действия пользователя.

    Работа с FSMFindImageName.
    """
    await state.clear()
    await message.answer(text=messages.CANCEL_MESSAGE)
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )


@router.message(FSMFindImageIcrawler.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMFindImageName.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.message(FSMFindImageIcrawler.title, F.text)
async def add_title(message: Message, state: FSMContext):
    """
    Просит пользователя ввести количество изображений.

    Работа с FSMFindImageName.
    """

    await state.update_data(title=message.text)
    await message.answer("🧑‍💻 Введите количество изображений для скачиания")
    await state.set_state(FSMFindImageIcrawler.count)


@router.message(FSMFindImageIcrawler.count, F.text)
async def get_image(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
    session,
):
    """
    Отправляет пользователю архив с изображениями.

    Работа с FSMFindImageName.
    """
    # Встаем в состояние spam для ответа пользователю при запроса
    await state.set_state(FSMFindImageIcrawler.spam)

    count_images: str = message.text
    data: Dict = await state.get_data()
    chat_id: int = message.chat.id

    # Проверяем ввел ли пользователь пололжительное число
    count_images = chek_number_is_positivity(number=count_images)
    if count_images.message:

        # Отправляем пользователю сообщение об ожидании ответа...
        await message.answer(
            f"{messages.WAIT_MESSAGE}",
            reply_markup=ReplyKeyboardRemove(),
        )
        logging_data = get_log()

        # Временный путь до архива с картинками
        path_archive: Path = (
            APP_DIR
            / "bot"
            / "temp"
            / Path(settings.NAME_FOR_TEMP_FOLDER)
            / str(message.from_user.id)
        )

        # Путь для сохранения архива
        path_save: Path = APP_DIR / "bot" / "temp" / settings.NAME_FOR_TEMP_FOLDER

        # Сообщение для отслеживания прогресса
        progress_message: Message = await bot.send_message(
            chat_id=chat_id,
            text=f"📸 Загружено 0 из {count_images.message}",
        )

        # функция для отслеживания прогресса
        async def notify_progress(
            crawler_download: int = 0,
            count_images: int = 0,
            complete: bool = False,
            source: str = "unknown",
        ):
            try:
                if not complete:
                    await progress_message.edit_text(
                        text=f"📸 Источник - {source}. Загружено {crawler_download} из {count_images}",
                    )
                else:
                    await progress_message.edit_text(
                        f"✅ Готово! Источник - {source}. Загружено {crawler_download} изображений."
                    )
            except Exception as err:
                print(err)

        # Источники получения изображений
        crawler: Crawler = Crawler(path=path_archive)
        google: Google = Google(
            query=data["title"],
            api_key=settings.GOOGLE_API_KEY,
            cx=settings.GOOGLE_CX,
        )

        # проходимся по источниками изображений
        for source in settings.IMAGE_SOURCES:
            adapter = get_images_adapter(
                source=source,
                session=session,
                google=google,
                crawler=crawler,
            )
            # Делаем запрос в service на получения архива
            archive_images: Union[
                ResponseData, NetworkResponseData
            ] = await find_name_image_service.recieve(
                title_image=data["title"],
                count_images=count_images.message,
                logging_data=logging_data,
                adapter=adapter,
                path_archive=path_archive,
                path_save=path_save,
                notify_progress=notify_progress,
                source=source,
            )
            if archive_images.message:
                await state.clear()
                await message.answer("⏳ Идет выгрузка архива в телеграм....")

                try:
                    retries = 3
                    for _ in range(retries):  # безопсано отправляем архив
                        try:
                            await bot.send_document(
                                chat_id=chat_id,
                                document=FSInputFile(str(archive_images.message)),
                                caption="🌆 Скачанные изображения",
                                reply_markup=ReplyKeyboardRemove(),
                                request_timeout=180,
                            )
                            break
                        except PermissionError:
                            asyncio.sleep(1)
                except TelegramNetworkError:
                    logging_data.info_logger.exception(
                        msg="Telegram timeout while uploading archive"
                    )
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"{telegam_emogi.red_cross} Произошла"
                        " ошибка при загрузке архива в телеграм...",
                    )

                await bot.send_message(
                    chat_id=chat_id,
                    text=messages.START_BOT_MESSAGE,
                    reply_markup=get_main_keyboards,
                )

                # удаляем архив
                archive = archive_images.message
                await save_delete_data(
                    list_path=[archive],
                    warning_logger=logging_data.warning_logger,
                )
                return
        await state.clear()
        await message.answer(f"{archive_images.error}\n{messages.TRY_REPSONSE_MESSAGE}")
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )

    else:
        await state.set_state(FSMFindImageIcrawler.count)
        await message.answer(
            text=f"{count_images.error}\n🧑‍💻 "
            "Введите, снова, количество изображений для скачиания",
            reply_markup=get_reply_cancel_button(),
        )
