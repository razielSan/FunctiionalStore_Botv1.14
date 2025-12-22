from typing import Dict

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.find_image.childes.find_name_image.settings import settings
from app.bot.modules.find_image.childes.find_name_image.services.find_image_name import (
    find_image_name_service,
)
from app.bot.modules.find_image.childes.find_name_image.logging import get_log
from app.settings.response import messages
from app.app_utils.keyboards import get_reply_cancel_button
from app.app_utils.chek import chek_number_is_positivity
from app.app_utils.filesistem import delete_data


router: Router = Router(name=__name__)


class FSMFindImageName(StatesGroup):
    """FSM для модели find_name_image"""

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
    await state.set_state(FSMFindImageName.title)


@router.message(FSMFindImageName.title, F.text == messages.CANCEL_TEXT)
@router.message(FSMFindImageName.count, F.text == messages.CANCEL_TEXT)
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


@router.message(FSMFindImageName.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMFindImageName.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.message(FSMFindImageName.title, F.text)
async def add_title(message: Message, state: FSMContext):
    """
    Просит пользователя ввести количество изображений.

    Работа с FSMFindImageName.
    """

    await state.update_data(title=message.text)
    await message.answer("🧑‍💻 Введите количество изображений для скачиания")
    await state.set_state(FSMFindImageName.count)


@router.message(FSMFindImageName.count, F.text)
async def get_image(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отправляет пользователю архив с изображениями.

    Работа с FSMFindImageName.
    """
    # Встаем в состояние spam для ответа пользователю при запроса
    await state.set_state(FSMFindImageName.spam)

    count_images: str = message.text
    data: Dict = await state.get_data()
    chat_id: int = message.chat.id

    # Проверяем ввел ли пользователь пололжительное число
    count_images = chek_number_is_positivity(number=count_images)
    if count_images.message:
        logging_data = get_log()

        # Делаем запрос в service на получения архива
        archive_images = await find_image_name_service.recieve(
            title_image=data["title"],
            count_images=count_images.message,
            message=message,
            logging_data=logging_data,
        )
        await state.clear()
        if archive_images.message:

            await message.answer("⏳ Идет выгрузка архива в телеграм....")

            # Отправляем архив пользователю
            await bot.send_document(
                chat_id=chat_id,
                document=FSInputFile(path=str(archive_images.message)),
                caption="Скаченные изображения",
                reply_markup=ReplyKeyboardRemove(),
            )
            await bot.send_message(
                chat_id=chat_id,
                text=messages.START_BOT_MESSAGE,
                reply_markup=get_main_keyboards,
            )

            # удаляем архив
            archive = archive_images.message
            delete_data(
                list_path=[archive, archive],
                warning_logger=logging_data.warning_logger,
            )
        else:
            await message.answer(
                f"{archive_images.error}\n{messages.TRY_REPSONSE_MESSAGE}"
            )
            await bot.send_message(
                chat_id=chat_id,
                text=messages.START_BOT_MESSAGE,
                reply_markup=get_main_keyboards,
            )

    else:
        await state.set_state(FSMFindImageName.count)
        await message.answer(
            text=f"{count_images.error}\n🧑‍💻 "
            "Введите, снова, количество изображений для скачиания",
            reply_markup=get_reply_cancel_button(),
        )
