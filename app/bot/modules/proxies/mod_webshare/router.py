from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from bot.modules.proxies.mod_webshare.settings import settings
from settings.response import messages


router: Router = Router(name="proxies.mod_webshare")


class FSMWebshare(StatesGroup):
    spam: State = State


@router.message(FSMWebshare.spam, F.text)
async def get_message_when_requested(message: Message):
    await message.reply(text=messages.WAIT_MESSAGE)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def webshare(call: CallbackQuery, state: FSMContext):

    await state.set_state(FSMWebshare.spam)

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )


# Register handlres below
