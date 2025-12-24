from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.core.response import InlineKeyboardData

from app.settings.response import telegam_emogi
from app.bot.modules.password.settings import settings


get_buttons_menu_password_inline_kb = get_total_buttons_inline_kb(
    list_inline_kb_data=[
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_1} Простой",
            callback_data=f"{settings.CALLBACK_PREFIX}-{settings.SIMPLE}",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_2} Сложный",
            callback_data=f"{settings.CALLBACK_PREFIX}-{settings.DIFFICULT}",
        ),
    ]
)
