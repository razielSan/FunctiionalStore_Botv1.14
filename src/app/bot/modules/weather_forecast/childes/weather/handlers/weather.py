from typing import Dict, Union

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.weather_forecast.childes.weather.settings import (
    settings,
    weather_translation_settings,
)
from app.bot.modules.weather_forecast.childes.weather.logging import get_log
from app.bot.modules.weather_forecast.childes.weather.api.weather_openwm import (
    weather_openwm_api,
)
from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.core.response import InlineKeyboardData
from app.settings.response import messages, telegam_emogi
from app.bot.modules.weather_forecast.childes.weather.services.weather import (
    weather_service,
)
from app.core.response import NetworkResponseData, ResponseData
from app.app_utils.keyboards import get_reply_cancel_button


router: Router = Router(name=__name__)


class FSMWeather(StatesGroup):
    """FSM для модели weather."""

    spam: State = State()
    future: State = (
        State()
    )  # флаг для проверки прогноза погоды на 5 днеий или на текущий
    city: State = State()


@router.message(FSMWeather.city, F.text == messages.CANCEL_TEXT)
async def cancel_weather_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отменяет все действия пользователя.

    Работа с FSMWeather.
    """
    await state.clear()
    await message.answer(text=messages.CANCEL_MESSAGE)
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )


@router.message(FSMWeather.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMWeather.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def weather(
    call: CallbackQuery,
) -> None:
    """
    Выводит инлайн клавиатуру пользователя для выбора вариантов погоды.

    Работа с FSMWeathe.
    """

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_total_buttons_inline_kb(
            list_inline_kb_data=[
                InlineKeyboardData(
                    text=settings.WEATHER_CALLBACK_BUTTON_1_TEXT,
                    callback_data=settings.WEATHER_CALLBACK_BUTTON_1_DATA,
                ),
                InlineKeyboardData(
                    text=settings.WEATHER_CALLBACK_BUTTON_2_TEXT,
                    callback_data=settings.WEATHER_CALLBACK_BUTTON_2_DATA,
                ),
            ],
        ),
    )


@router.callback_query(
    StateFilter(None), F.data.startswith(settings.WEATHER_CALLBACK_PREFIX)
)
async def add_city(call: CallbackQuery, state: FSMContext):
    """
    Просит пользователя ввести название города.

    Работа с FSMWeather
    """

    await call.message.edit_reply_markup(reply_markup=None)

    data_weather = call.data.split(" ")[1]

    await call.message.answer(
        f"{telegam_emogi.pencil} Введите названия города",
        reply_markup=get_reply_cancel_button(),
    )

    # Определяем прогноз погоды на п 5 дней или текущий
    future: bool = True if data_weather == settings.WEATHER_CALLBACK_DATA_2 else False

    await state.set_state(FSMWeather.future)
    await state.update_data(future=future)
    await state.set_state(FSMWeather.city)


@router.message(FSMWeather.city, F.text)
async def get_weather(
    message: Message,
    state: FSMContext,
    bot: Bot,
    session,
    get_main_keyboards,
):
    """
    Отправляет пользователю прогноз погоды на 5 дней или на текущий день.

    Работа с FSMWeather.
    """

    # Встаем в состояние spam для отправки сообщения пользователю при запросе
    await state.set_state(FSMWeather.spam)

    await message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    # Формируем необходимые данные
    logging_data = get_log()
    chat_id: int = message.chat.id
    data: Dict = await state.get_data()
    future: bool = data["future"]
    url_geolocated_openweathermap: str = settings.ULR_GEOLOCATED_OPENWEATHERMAP.format(
        query=message.text,
        appid=settings.APPID,
    )

    # Опредяем url - текущий или на 5 дней
    url_weather: str = (
        settings.URL_FEATURE_OPENWEATHERMAP
        if future is True
        else settings.URL_CURRENT_OPENWEATHERMAP
    )

    result_weather: Union[
        NetworkResponseData, ResponseData
    ] = await weather_service.recieve(
        city=message.text,
        logging_data=logging_data,
        url_weather=url_weather,
        url_geolocated_openweathermap=url_geolocated_openweathermap,
        api_openweathermap=settings.APPID,
        session=session,
        future=future,
        weather_openwm_api=weather_openwm_api,
        weather_translation=weather_translation_settings.weather_translation,
    )
    await state.clear()
    if result_weather.message:
        await message.answer(text=result_weather.message)
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await message.answer(
            text=f"{result_weather.error}\n\n{messages.TRY_REPSONSE_MESSAGE}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
