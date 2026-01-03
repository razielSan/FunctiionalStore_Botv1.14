from typing import Union

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.weather_forecast.childes.aqi.settings import settings, aqi_settings
from app.bot.modules.weather_forecast.childes.aqi.logging import get_log
from app.bot.modules.weather_forecast.childes.aqi.api.aqi_openwm import aqi_openwm_api
from app.settings.response import messages, telegam_emogi
from app.bot.modules.weather_forecast.childes.aqi.services.aqi import aqi_service
from app.core.response import NetworkResponseData, ResponseData
from app.app_utils.keyboards import get_reply_cancel_button


router: Router = Router(name=__name__)


class FSMAqi(StatesGroup):
    """FSM для модели aqi."""

    spam: State = State()
    city: State = State()


@router.message(FSMAqi.city, F.text == messages.CANCEL_TEXT)
async def cancel_aqi_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отменяет все действия пользователя.

    Работа с FSMAqi.
    """
    await state.clear()
    await message.answer(text=messages.CANCEL_MESSAGE)
    await bot.send_message(
        chat_id=message.chat.id,
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )


@router.message(FSMAqi.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMAqi.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def aqi(
    call: CallbackQuery,
    state: FSMContext,
) -> None:
    """
    Просит пользователя ввести название города.

    Работа с FSMAqi.
    """

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"{telegam_emogi.pencil} Введите названия города",
        reply_markup=get_reply_cancel_button(),
    )

    await state.set_state(FSMAqi.city)


@router.message(FSMAqi.city, F.text)
async def get_aqi(
    message: Message,
    state: FSMContext,
    bot: Bot,
    session,
    get_main_keyboards,
):
    """
    Отправляет данные об уровне загрязнения воздуха в городе.

    Работа с FSMAqi
    """

    # Встаем в состояние spam для отправки сообщения пользователю при запросе
    await state.set_state(FSMAqi.spam)

    await message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    # Формируем необходимые данные
    logging_data = get_log()
    chat_id: int = message.chat.id

    result_aqi: Union[NetworkResponseData, ResponseData] = await aqi_service.recieve(
        city=message.text,
        api_openweathermap=settings.APPID,
        url_air_pollution=settings.URL_AIR_POLLUTION,
        url_geolocated_openweathermap=settings.ULR_GEOLOCATED_OPENWEATHERMAP.format(
            query=message.text,
            appid=settings.APPID,
        ),
        air_pollution=aqi_settings.AIR_POLLUTION,
        aqi=aqi_settings.AQI,
        session=session,
        logging_data=logging_data,
        aqi_openwm_api=aqi_openwm_api,
    )
    await state.clear()
    if result_aqi.message:
        await message.answer(text=result_aqi.message)
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await message.answer(
            text=f"{result_aqi.error}\n\n{messages.TRY_REPSONSE_MESSAGE}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
