from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.password.settings import settings
from app.bot.modules.password.keyboards.inline_kb import (
    get_buttons_menu_password_inline_kb,
)
from app.bot.modules.password.services.password import password_service
from app.bot.modules.password.logging import get_log
from app.core.response import ResponseData, LoggingData, InlineKeyboardData
from app.settings.response import messages
from app.app_utils.keyboards import get_total_buttons_inline_kb


router: Router = Router(name=__name__)


@router.message(StateFilter(None), F.text == settings.MENU_REPLY_TEXT)
async def password(message: Message, bot: Bot) -> None:
    """Возвращает пользователю клавиатуру с выбором варинтов генерации пароля."""
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass
    await message.answer(
        text=messages.OPTIONS_BOT_MESSAGE,
        reply_markup=get_buttons_menu_password_inline_kb,
    )


class FSMPassword(StatesGroup):
    """FSM для модуля password."""

    spam: State = State()


@router.message(FSMPassword.spam, F.text)
async def get_message_is_state_spam(message: Message):
    """
    Отправка пользователю сообщения при вводе текста во время запроса.

    Работа с FSMPassword.
    """
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(F.data.startswith(f"{settings.CALLBACK_PREFIX}-"))
async def get_buttons_step_password(call: CallbackQuery):
    """
    Отправляет пользователю инлайн клавиатуру с выбором варианта сложности пароля.

    Работа с FSMPassword.
    """
    await call.message.edit_reply_markup(reply_markup=None)

    type_password = call.data.split("-")[1]  # достаем тип пароля

    # Формируем инлайн клавиатуру с типом пароля и шагом
    inline_kb = get_total_buttons_inline_kb(
        list_inline_kb_data=[
            InlineKeyboardData(
                text="1", callback_data=f"{settings.CALLBACK_PREFIX} {type_password} 1"
            ),
            InlineKeyboardData(
                text="2", callback_data=f"{settings.CALLBACK_PREFIX} {type_password} 2"
            ),
            InlineKeyboardData(
                text="3", callback_data=f"{settings.CALLBACK_PREFIX} {type_password} 3"
            ),
            InlineKeyboardData(
                text="4", callback_data=f"{settings.CALLBACK_PREFIX} {type_password} 4"
            ),
        ],
        quantity_button=2,
    )
    await call.message.answer(
        text="🚦 Выберите шаг для пароля",
        reply_markup=inline_kb,
    )


@router.callback_query(
    F.data.startswith(f"{settings.CALLBACK_PREFIX} {settings.SIMPLE}")
)
@router.callback_query(
    F.data.startswith(f"{settings.CALLBACK_PREFIX} {settings.DIFFICULT}")
)
async def get_generate_passwords(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    get_main_keyboards,
):
    """
    Отправляет пользователю сгенерированные пароли.

    Работа с FSMPassword.
    """

    await call.message.edit_reply_markup(reply_markup=None)  # удаляем инлайн клавиатуру

    # Встаем в состояние spam для отправки сообщения пользователю во время запроса
    await state.set_state(FSMPassword.spam)

    chat_id: int = call.message.chat.id

    # Подготавливаем данные для service
    data_password = call.data.split(" ")
    type_passowrd: str = data_password[1]  # тип пароля
    step: int = int(data_password[2])
    logging_data: LoggingData = get_log()

    # делаем запрос в service на получение паролей
    password: ResponseData = await password_service.recieve(
        type_password=type_passowrd, step=step, logging_data=logging_data
    )
    await state.clear()
    if password.message:
        await call.message.answer(password.message)
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_keyboards,
        )
    else:
        await call.message.answer(
            text=f"{password.error}\n{messages.TRY_REPSONSE_MESSAGE}",
            reply_markup=get_main_keyboards,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=messages.OPTIONS_BOT_MESSAGE,
            reply_markup=get_buttons_menu_password_inline_kb,
        )
