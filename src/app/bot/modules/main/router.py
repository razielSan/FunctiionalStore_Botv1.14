from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters.state import StateFilter

from app.settings.response import messages
from app.bot.core.init_logging import bot_info_logger, bot_warning_logger


router: Router = Router(name="main")


def register(
    dp: Dispatcher,
    parent_router: bool,
    root_router: object,
) -> None:
    if not parent_router:  # если роутер корневой
        # Проверка на то что этот роутер ни к кому не подключен
        if getattr(router, "parent_router", None) is None:
            dp.include_router(router)
            bot_info_logger.info(f"\n[Auto] Root router inculde into dp: {router}")
        else:
            bot_warning_logger.warning(
                f"\n[Auto] Root router already attached: {router}"
            )

    else:
        if getattr(router, "parent_router", None) is None:
            root_router.include_router(router)
            bot_info_logger.info(
                f"\n[Auto] Child router inculded into {root_router}: {router}"
            )
        else:
            bot_warning_logger.warning(
                f"\n[Auto] Child router already attached: {router}"
            )


@router.message(
    StateFilter(None),
    F.text == "/start",
)
async def main(
    message: Message,
    bot: Bot,
    get_main_keyboards,
) -> None:
    """Отправляет пользователю reply клавиатуру главного меню."""
    # Удаляет сообщение которое было последним
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await message.answer(
        text=messages.START_BOT_MESSAGE,
        reply_markup=get_main_keyboards,
    )
