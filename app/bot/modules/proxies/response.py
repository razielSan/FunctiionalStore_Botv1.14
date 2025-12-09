from pathlib import Path

from app_utils.modules import get_child_modules_settings_inline_data
from app_utils.keyboards import get_total_buttons_inline_kb

inline_data = get_child_modules_settings_inline_data(
    module_path=Path("bot/modules/proxies")
)
for data in inline_data:
    print(data)
get_keyboards_menu_buttons = get_total_buttons_inline_kb(
    list_inline_kb_data=inline_data, quantity_button=1
)
