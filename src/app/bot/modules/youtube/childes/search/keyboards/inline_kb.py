from app.app_utils.keyboards import get_total_buttons_inline_kb
from app.core.response import InlineKeyboardData
from app.settings.response import telegam_emogi
from app.bot.modules.youtube.childes.search.settings import settings

get_buttons_search_inline_kb = get_total_buttons_inline_kb(
    list_inline_kb_data=[
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_1} По дате создания",
            callback_data=f"{settings.CALLBACK_PREFIX} sort date",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_2} По релевантности",
            callback_data=f"{settings.CALLBACK_PREFIX} sort relevance",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_3} По рейтингу",
            callback_data=f"{settings.CALLBACK_PREFIX} sort rating",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_4} По названию",
            callback_data=f"{settings.CALLBACK_PREFIX} sort title",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_5} По просмотрам",
            callback_data=f"{settings.CALLBACK_PREFIX} sort viewCount",
        ),
        InlineKeyboardData(
            text=f"{telegam_emogi.digit_6 } Каналы",
            callback_data=f"{settings.CALLBACK_PREFIX} sort channel",
        ),
    ],
    quantity_button=2,
)
