from aiogram.types import InlineKeyboardMarkup

from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.core.response import InlineKeyboardData
from app.settings.response import telegam_emogi
from app.bot.modules.proxies.childes.free_proxy.settings import settings


get_free_proxy_keyboards_inline_kb: InlineKeyboardMarkup = get_total_buttons_inline_kb(
    list_inline_kb_data=[
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_1} http proxy (часто встречаются)",
            callback_data=f"{settings.CALLBACK_PREFIX}http",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_2} https proxy (редко встречаются)",
            callback_data=f"{settings.CALLBACK_PREFIX}https",
        ),
    ]
)
