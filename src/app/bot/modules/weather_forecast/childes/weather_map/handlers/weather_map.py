from typing import Union
from pathlib import Path
import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import folium

from app.bot.modules.weather_forecast.childes.weather_map.settings import settings
from app.bot.modules.weather_forecast.childes.weather_map.logging import get_log
from app.bot.modules.weather_forecast.childes.weather_map.api.weather_map_openwm import (
    weather_map_openwm_api,
)
from app.settings.response import messages
from app.bot.modules.weather_forecast.childes.weather_map.services.weather_map import (
    weather_map_service,
)
from app.core.response import NetworkResponseData, ResponseData
from app.bot.core.paths import bot_path


router: Router = Router(name=__name__)


class FSMWeatherMap(StatesGroup):
    """FSM для модели weather_map."""

    spam: State = State()


@router.message(FSMWeatherMap.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMWeather.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def weather_map(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    session,
    get_main_keyboards,
):
    """
    Отправляет пользователю карту погоды.

    Работа с FSMWeatherMap.
    """

    await state.set_state(FSMWeatherMap.spam)

    await call.message.edit_reply_markup(
        reply_markup=None,
    )

    await call.message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    # Подготовливаем данные для service
    chat_id: int = call.message.chat.id
    logging_data = get_log()
    path_to_weather_map: Path = (
        bot_path.BOT_DIR
        / "temp"
        / Path(settings.NAME_FOR_TEMP_FOLDER)
        / settings.NAME_WEATHER_MAP
    )

    result_weather_map: Union[
        NetworkResponseData, ResponseData
    ] = await weather_map_service.recieve(
        api_openweathermap=settings.APPID,
        weather_layers=settings.WEATHER_LAYERS,
        path_to_weathermap=path_to_weather_map,
        session=session,
        logging_data=logging_data,
        folium=folium,
        weather_map_openwm_api=weather_map_openwm_api,
        url_weather_map=settings.URL_WEATHER_MAPS.format(appid=settings.APPID),
    )

    await state.clear()
    if result_weather_map.message:
        await bot.send_document(
            chat_id=chat_id,
            document=FSInputFile(
                path=result_weather_map.message,
            ),
            caption="🌈 Карта Погоды",
        )
        await call.message.answer(
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await call.message.answer(
            text=f"{result_weather_map.error}\n\n{messages.TRY_REPSONSE_MESSAGE}"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
