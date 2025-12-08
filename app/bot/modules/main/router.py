from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from settings.response import messages


router: Router = Router(name="main")


@router.message(
    StateFilter(None),
    F.text == "/start",
)
async def main(message: Message, bot: Bot, main_keyboards) -> None:
    """Отправляет ползователю reply клавиатуру главного меню."""
    print("aaaa")
    # Удаляет сообщение которое было последним
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await message.answer(
        text=messages.START_BOT_MESSAGE,
        reply_markup=main_keyboards,
    )
