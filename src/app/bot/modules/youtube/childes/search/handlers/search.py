from typing import Dict, List

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.youtube.childes.search.settings import settings
from app.bot.modules.youtube.childes.search.logging import get_log
from app.bot.modules.youtube.childes.search.services.search import (
    search_youtube_service,
)
from app.bot.modules.youtube.childes.search.keyboards.inline_kb import (
    get_buttons_search_inline_kb,
)
from app.settings.response import messages
from app.core.response import NetworkResponseData
from app.app_utils.keyboards import (
    get_reply_cancel_button,
    get_button_for_forward_or_back,
)
from app.bot.modules.youtube.childes.search.extensions import get_service


router: Router = Router(name=__name__)


class FSMYoutubeSearch(StatesGroup):
    """FSM для модели search."""

    spam: State = State()
    title: State = State()
    choise_sort: State = State()
    list_result_video: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def search(call: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    """Возвращает пользователю клавиатуру с выбором вариантов поиска."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text="🤔 Выберите вариант поиска...",
        reply_markup=get_reply_cancel_button(),
    )
    await bot.send_message(
        chat_id=call.message.chat.id,
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_buttons_search_inline_kb,
    )

    await state.set_state(FSMYoutubeSearch.choise_sort)


@router.message(FSMYoutubeSearch.title, F.text == messages.CANCEL_TEXT)
@router.message(FSMYoutubeSearch.choise_sort, F.text == messages.CANCEL_TEXT)
@router.message(FSMYoutubeSearch.list_result_video, F.text == messages.CANCEL_TEXT)
async def cancel_search_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отменяет все действия пользователя.

    Работа с FSMYoutubeSearch.
    """

    # для удаления инлайн клавиатуры
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass
    await state.clear()
    await message.answer(text=messages.CANCEL_MESSAGE)
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )


@router.message(FSMYoutubeSearch.spam, F.text)
@router.message(FSMYoutubeSearch.choise_sort, F.text)
@router.message(FSMYoutubeSearch.list_result_video, F.text)
async def get_message_is_state_spam(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """
    Отправка пользователю сообщения при вводе текста, при нахождении
    в соcтояниях spam,choise_sort,list_result_video

    Работа с FSMYoutubeSearch.
    """

    current_state = await state.get_state()

    if (
        current_state == "FSMYoutubeSearch:choise_sort"
        or current_state == "FSMYoutubeSearch:list_result_video"
    ):  # если пользователь в состоянии выбора варианта
        # видео или при пролистывании полученных результатов
        await message.reply(text=messages.MENU_CANCEL_MESSAGE)
    elif current_state == "FSMYoutubeSearch:spam":
        await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(
    FSMYoutubeSearch.choise_sort, F.data.startswith(f"{settings.CALLBACK_PREFIX} ")
)
async def add_choise_sort(call: CallbackQuery, state: FSMContext):
    """
    Просит пользователя ввести название видео для поиска.

    Работа с FSMYoutubeSearch.
    """

    await call.message.edit_reply_markup(reply_markup=None)

    choise_sort = call.data.split(" ")[2]

    await call.message.answer("✏ Введите название видео...")
    await state.update_data(choise_sort=choise_sort)
    await state.set_state(FSMYoutubeSearch.title)


@router.message(FSMYoutubeSearch.title, F.text)
async def get_search_result_video(
    message: Message, state: FSMContext, bot: Bot, get_main_keyboards
):
    """
    Возвращает пользователю результат поиска видео.

    Работа с FSMYoutubeSearch.
    """
    await state.set_state(FSMYoutubeSearch.spam)

    data: Dict = await state.get_data()
    sort: str = data["choise_sort"]

    logging_data = get_log()

    service = get_service(api_key=settings.API_KEY)

    youtube_video: NetworkResponseData = await search_youtube_service.recieve(
        name_video=message.text,
        logging_data=logging_data,
        sort=sort,
        service=service,
        youtube_channel_url=settings.CHANNEL_URL,
        youtube_video_url=settings.VIDEO_URL,
    )
    if youtube_video.message:

        await state.set_state(FSMYoutubeSearch.list_result_video)
        await state.update_data(list_result_video=youtube_video.message)
        await message.answer(
            text=youtube_video.message[0],
            reply_markup=get_button_for_forward_or_back(
                prefix=settings.END_PREFIX, list_data=youtube_video.message
            ),
        )
    else:
        await state.clear()
        await message.answer(
            text=f"{youtube_video.error}\n{messages.TRY_REPSONSE_MESSAGE}",
        )
        await bot.send_message(
            text=messages.START_BOT_MESSAGE,
            chat_id=message.chat.id,
            reply_markup=get_main_keyboards,
        )


@router.callback_query(
    FSMYoutubeSearch.list_result_video, F.data.startswith(settings.END_PREFIX)
)
async def finish_find_video(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
):
    """
    Пролистывает найденные видео.

    Работа с FSM FindVideo.
    """

    _, _, count = call.data.split(" ")
    data: Dict = await state.get_data()
    video_search_list: List = data["list_result_video"]

    await bot.edit_message_text(
        text=video_search_list[int(count)],
        reply_markup=get_button_for_forward_or_back(
            prefix=settings.END_PREFIX,
            list_data=video_search_list,
            indeх=int(count),
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
