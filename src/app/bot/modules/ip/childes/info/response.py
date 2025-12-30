# Responses, strings, text for module ip.childes.info
from pathlib import Path

from app.app_utils.module_loader.loader import get_child_modules_settings_inline_data
from app.app_utils.keyboards import get_total_buttons_inline_kb


inline_data = get_child_modules_settings_inline_data(
    module_path=Path("D:/ProgrammingProjects/Python/Bot/Project/BOT_PROJECT/func_store_botV1.4/src/app/bot/modules/ip/childes/info/childes"),
    root_package="app.bot.modules.ip.childes.info.childes"
)

get_keyboards_menu_buttons = get_total_buttons_inline_kb(
    list_inline_kb_data=inline_data, quantity_button=1
)
